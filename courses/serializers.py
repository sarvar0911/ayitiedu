from rest_framework import serializers
from .models import ChatMessage, Course, Enrollment, Lesson, Module, StudentLessonProgress
from django.conf import settings
from urllib.parse import urljoin
import base64
from django.core.files.base import ContentFile

class Base64ImageField(serializers.ImageField):
    """
    Custom field for handling image uploads via base64 and providing URLs
    """
    def to_representation(self, value):
        request = self.context.get('request')
        full_url = urljoin(request.build_absolute_uri('/'), value.url) if request else f"{settings.MEDIA_URL}{value.name}"
        return {
            "src": full_url
        } if value else None

    def to_internal_value(self, data):
        """
        Convert base64 string back to an image file.
        """
        if isinstance(data, dict) and 'base64' in data:
            try:
                format, imgstr = data['base64'].split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')
            except (TypeError, ValueError) as e:
                raise serializers.ValidationError("Invalid base64 image format.") from e
        return super().to_internal_value(data)

class BaseCourseSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Course
        fields = ['id', 'image', 'title', 'short_description']


class CourseListSerializer(BaseCourseSerializer):
    class Meta(BaseCourseSerializer.Meta):
        pass


class CourseWithAccessSerializer(BaseCourseSerializer):
    has_access = serializers.SerializerMethodField()

    class Meta(BaseCourseSerializer.Meta):
        fields = BaseCourseSerializer.Meta.fields + ['has_access']

    def get_has_access(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Enrollment.objects.filter(course=obj, user=user, has_access=True).exists()
        return False


class CourseDetailSerializer(BaseCourseSerializer):
    class Meta(BaseCourseSerializer.Meta):
        fields = BaseCourseSerializer.Meta.fields + ['description', 'test_question_count']


class ModuleListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'title', 'description']


class ModuleSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'title']


class LessonDetailSerializer(serializers.ModelSerializer):
    completed_date = serializers.DateTimeField(source='student_progress.completed_date', read_only=True)
    started_date = serializers.DateTimeField(source='student_progress.started_date', read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'module', 'title', 'description', 'pdf', 
            'video_url', 'presentation', 'completed_date', 'started_date'
        ]


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'description', 'pdf', 'video_url', 'presentation']


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['contract_file', 'course', 'user', 'has_access', 'completed', 'started_date', 'completed_date']


class ReplyToSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'message']


class ChatMessageSerializer(serializers.ModelSerializer):
    reply = ReplyToSerializer(read_only=True)
    user = serializers.StringRelatedField()  # To show the username in responses
    reply_id = serializers.PrimaryKeyRelatedField(queryset=ChatMessage.objects.all(), write_only=True, required=False, allow_null=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'user', 'message', 'date', 'type', 'reply', 'reply_id']

    def create(self, validated_data):
        reply_message = validated_data.pop('reply_id', None)
        chat_message = ChatMessage.objects.create(**validated_data, reply=reply_message)
        return chat_message


class StudentLessonProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentLessonProgress
        fields = ['lesson', 'student', 'started_date', 'completed_date']
