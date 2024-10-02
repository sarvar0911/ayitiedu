from django.http import Http404
from django.conf import settings
from django.db.models import Q
from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import get_object_or_404
from .models import ChatMessage, Course, Lesson, Module
from .serializers import (
    ChatMessageSerializer, CourseDetailSerializer, CourseListSerializer, 
    CourseWithAccessSerializer, LessonDetailSerializer, 
    LessonSerializer, ModuleListSerializer, ModuleSummarySerializer
)
from .services import ContractService, EnrollmentService, StudentLessonProgressService, StatsService, ChatService


class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all().prefetch_related('modules')
    serializer_class = CourseWithAccessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        title = self.request.query_params.get('title')
        price = self.request.query_params.get('price')
        queryset = super().get_queryset()

        if title:
            queryset = queryset.filter(title__icontains=title)
        if price:
            queryset = queryset.filter(price=price)
        return queryset


class CoursesAllListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseListSerializer
    permission_classes = [AllowAny]


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.all().prefetch_related('modules')
    serializer_class = CourseDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


class ModuleListByCourseView(generics.ListAPIView):
    serializer_class = ModuleListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        course_id = self.request.query_params.get('course_id')
        if not course_id:
            raise Http404("course_id parameter is required.")
        return Module.objects.filter(course_id=course_id).select_related('course')


class AllModuleListByCourseView(generics.ListAPIView):
    serializer_class = ModuleListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        course_id = self.request.query_params.get('course_id')
        if not course_id:
            raise Http404("course_id parameter is required.")
        return Module.objects.filter(course_id=course_id).select_related('course')


class ModuleDetailView(generics.RetrieveAPIView):
    queryset = Module.objects.all().select_related('course')
    serializer_class = ModuleSummarySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


class LessonListByModuleView(generics.ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        module_id = self.request.query_params.get('module_id')
        if not module_id:
            raise Http404("module_id parameter is required.")
        return Lesson.objects.filter(module_id=module_id).select_related('module')


class RegisterCourseView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        enrollment, contract_filename = EnrollmentService.register_user_for_course(request.user, course_id)

        if contract_filename:
            contract_url = request.build_absolute_uri(f"{settings.MEDIA_URL}course_files/{contract_filename}")
            return Response({
                "message": "Student registered successfully.",
                "contract_url": contract_url
            }, status=status.HTTP_200_OK)

        return Response({"message": "You are already registered for this course."}, status=status.HTTP_200_OK)


class StatsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        stats = StatsService.get_statistics()
        return Response(stats)


class LessonDetailView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all().select_related('module')
    serializer_class = LessonDetailSerializer
    lookup_field = 'id'


class StudentLessonStartView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            progress = StudentLessonProgressService.start_lesson(request.user, lesson_id)
            
            if progress is None:
                return Response({
                    "message": "Lesson already started.",
                    "lesson_title": lesson.title
                }, status=status.HTTP_200_OK)

            return Response({
                "message": "Lesson started successfully.",
                "lesson_title": lesson.title,
                "started_date": progress.started_date,
                "progress": "in progress"
            }, status=status.HTTP_200_OK)

        except Lesson.DoesNotExist:
            return Response({"error": "Lesson not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudentLessonFinishView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, lesson_id):
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            progress = StudentLessonProgressService.finish_lesson(request.user, lesson_id)
            
            if progress is None:
                return Response({
                    "message": "Lesson already completed.",
                    "lesson_title": lesson.title
                }, status=status.HTTP_200_OK)

            return Response({
                "message": "Lesson completed successfully.",
                "lesson_title": lesson.title,
                "completed_date": progress.completed_date,
                "progress": "completed"
            }, status=status.HTTP_200_OK)

        except Lesson.DoesNotExist:
            return Response({"error": "Lesson not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class SendMessageView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatMessageSerializer

    def perform_create(self, serializer):
        # Get module and user
        module = Module.objects.get(id=self.kwargs['module_id'])
        user = self.request.user
        
        # Save the chat message
        chat_message = serializer.save(module=module, user=user)
        
        # Trigger WebSocket message broadcast
        self.broadcast_message(chat_message)

    def broadcast_message(self, chat_message):
        channel_layer = get_channel_layer()
        group_name = f"module_{chat_message.module.id}"

        # Serialize the message for WebSocket clients
        message_data = {
            "type": "chat_message",
            "message": chat_message.message,
            "user": chat_message.user.username,
            "type": chat_message.type,
            "reply": chat_message.reply.id if chat_message.reply else None
        }

        # Broadcast the message to the WebSocket group
        async_to_sync(channel_layer.group_send)(group_name, message_data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            

class ChatListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        module_id = self.kwargs.get('module_id')
        module = get_object_or_404(Module, id=module_id)

        second_user = self.request.query_params.get('student')
        if not second_user:
            second_user = module.course.teacher

        return ChatMessage.objects.filter(
            module_id=module_id
        ).filter(
            Q(user=self.request.user) | Q(user=second_user)
        ).select_related('module', 'user').order_by('date')
