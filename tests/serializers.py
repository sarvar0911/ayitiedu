from rest_framework import serializers
from .models import TestEnrollment, TestQuestion, TestAnswer, Feedback
import base64
from django.core.files.base import ContentFile
from urllib.parse import urljoin
from django.conf import settings
from courses.serializers import CourseListSerializer


class Base64ImageWithURLField(serializers.ImageField):
    def to_representation(self, value):
        if value:
            try:
                request = self.context.get('request')
                full_url = urljoin(request.build_absolute_uri('/'), value.url) if request else f"{settings.MEDIA_URL}{value.name}"
                return {
                    "base64": f"data:image/{value.name.split('.')[-1]};base64,{base64.b64encode(value.read()).decode()}",
                    "src": full_url
                }
            except Exception:
                raise serializers.ValidationError("Error processing image.")
        return None

    def to_internal_value(self, data):
        if isinstance(data, dict) and 'base64' in data:
            try:
                format, imgstr = data['base64'].split(';base64,')
                ext = format.split('/')[-1]
                data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
            except (TypeError, ValueError):
                raise serializers.ValidationError("Invalid base64 image format.")
        return super().to_internal_value(data)


class TestAnswerSerializer(serializers.ModelSerializer):
    correct_answer = serializers.BooleanField(read_only=True)

    class Meta:
        model = TestAnswer
        fields = ['id', 'answer', 'correct_answer']


class TestQuestionDetailSerializer(serializers.ModelSerializer):
    answers = TestAnswerSerializer(many=True, required=False)
    image = Base64ImageWithURLField(required=True)  # Base64 required as per request

    class Meta:
        model = TestQuestion
        fields = ['id', 'question_text', 'question_type', 'image', 'answers']


class TestEnrollmentDetailSerializer(serializers.ModelSerializer):
    questions = TestQuestionDetailSerializer(many=True)

    class Meta:
        model = TestEnrollment
        fields = ['id', 'started_at', 'type', 'total_questions', 'finished', 'questions']


class TestQuestionSerializer(serializers.ModelSerializer):
    image = Base64ImageWithURLField(required=True)  # Base64 required

    class Meta:
        model = TestQuestion
        fields = ['id', 'question_text', 'question_type', 'image']


class TestEnrollmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = TestEnrollment
        fields = ['id', 'student', 'course', 'total_questions', 'correct_answers', 'type', 'started_at', 'finished']
        read_only_fields = ['id', 'started_at']  

    def validate(self, data):
        if TestEnrollment.objects.filter(
            student=data['student'],
            course=data['course'],
            type=data['type']
        ).exists():
            raise serializers.ValidationError("A test enrollment already exists for this student, course, and test type.")
        return data


from rest_framework import serializers
from .models import Feedback
from django.utils.translation import gettext_lazy as _


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['full_name', 'feedback_text', 'rating', 'course']

    def validate_rating(self, value):
        if value > 5:
            raise serializers.ValidationError(_("Rating cannot be more than 5."))
        return value

    def validate(self, data):
        request = self.context.get('request')
        user = request.user

        if Feedback.objects.filter(user=user, course=data['course']).exists():
            raise serializers.ValidationError(_("Feedback already submitted for this course."))

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class StudentResultDetailSerializer(serializers.ModelSerializer):
    course = CourseListSerializer()

    class Meta:
        model = TestEnrollment
        fields = ['course', 'started_at', 'type', 'total_questions', 'finished', 'correct_answers']


class StudentResultSerializer(serializers.ModelSerializer):
    course = CourseListSerializer()
    certificate_file = serializers.FileField()

    class Meta:
        model = TestEnrollment
        fields = ['id', 'total_questions', 'correct_answers', 'finished', 'type', 'course', 'certificate_file']
