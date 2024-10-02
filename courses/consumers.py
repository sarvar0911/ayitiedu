from channels.generic.websocket import AsyncWebsocketConsumer
import json
from asgiref.sync import sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from .models import Module, ChatMessage
from .serializers import ChatMessageSerializer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract module ID from the URL route
        self.module_id = self.scope['url_route']['kwargs']['module_id']
        self.module_group_name = f"module_{self.module_id}"

        # Authenticate the user using token from the headers
        headers = dict(self.scope['headers'])
        token = headers.get(b'authorization', b'').decode().split('Bearer ')[-1]
        user = await self.authenticate_user(token)
        self.scope['user'] = user

        # Add user to the channel group if authenticated
        if user.is_authenticated:
            await self.channel_layer.group_add(self.module_group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.module_group_name, self.channel_name)

    async def receive(self, text_data):
        # WebSockets won’t handle message sending (handled via HTTP)
        pass

    async def chat_message(self, event):
        # Broadcast message data to the WebSocket clients
        message = event['message']
        user = event['user']
        type_ = event['type']
        reply = event.get('reply')

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'user': user,
            'type': type_,
            'reply': reply
        }))

    async def authenticate_user(self, token):
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            return await self.get_user_from_id(user_id)
        except Exception:
            return AnonymousUser()

    @sync_to_async
    def get_user_from_id(self, user_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.get(id=user_id)
