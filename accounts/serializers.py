import base64
from urllib.parse import urljoin
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Teacher

User = get_user_model()


class Base64ImageWithURLField(serializers.ImageField):
    def to_representation(self, value):
        """
        Return both the Base64-encoded image and its URL.
        """
        if value:
            try:
                request = self.context.get('request')
                # Generate full URL for the image
                if request:
                    full_url = urljoin(request.build_absolute_uri('/'), value.url)
                else:
                    full_url = f"{settings.MEDIA_URL}{value.name}"

                # Read and encode image in Base64
                with value.open('rb') as image_file:
                    encoded_image = base64.b64encode(image_file.read()).decode()

                return {
                    "base64": f"data:image/{value.name.split('.')[-1]};base64,{encoded_image}",
                    "src": full_url
                }
            except Exception as e:
                raise serializers.ValidationError("Error processing image.") from e
        return None

    def to_internal_value(self, data):
        """
        Decode Base64 image before saving it.
        """
        if isinstance(data, dict) and 'base64' in data:
            try:
                format, imgstr = data['base64'].split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            except (TypeError, ValueError) as e:
                raise serializers.ValidationError("Invalid base64 image format.") from e
        return super().to_internal_value(data)


class TeacherSerializer(serializers.ModelSerializer):
    picture = Base64ImageWithURLField()

    class Meta:
        model = Teacher
        fields = ['fullname', 'speciality', 'picture']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'role')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, error_messages={
        "min_length": "Password must be at least 8 characters long."
    })

    class Meta:
        model = User
        fields = ('username', 'password')

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        """
        Create a new user and return JWT tokens.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        refresh = RefreshToken.for_user(user)
        return {
            'username': user.username,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)

    def validate(self, data):
        """
        Validate user credentials and return JWT tokens.
        """
        username = data.get('username')
        password = data.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            raise serializers.ValidationError("Invalid username or password.")

        refresh = RefreshToken.for_user(user)
        return {
            'username': user.username,
            'role': user.role,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
