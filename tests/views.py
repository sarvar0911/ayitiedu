from datetime import timezone
from django.http import FileResponse
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ValidationError
from django.shortcuts import get_object_or_404
from courses.models import Course, Enrollment
from tests.services import CertificateService, TestGenerationService, TestSubmissionService
from .models import Feedback, TestEnrollment
from .serializers import (
    FeedbackSerializer,
    TestEnrollmentSerializer,
    TestEnrollmentDetailSerializer,
    StudentResultDetailSerializer,
)


class RetrieveObjectMixin:
    def get_object_or_404(self, model, **kwargs):
        return get_object_or_404(model, **kwargs)


class StudentResultsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TestEnrollmentSerializer

    def get_queryset(self):
        return TestEnrollment.objects.filter(student=self.request.user)


class StudentResultsDetailView(RetrieveObjectMixin, generics.RetrieveAPIView):
    serializer_class = StudentResultDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TestEnrollment.objects.filter(student=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if not instance.finished:
            return Response(self.get_serializer(instance).data)

        if not instance.certificate_file:
            CertificateService.create_certificate(instance)
            instance.refresh_from_db()

        return self._serve_certificate(instance)

    @staticmethod
    def _serve_certificate(instance):
        response = FileResponse(instance.certificate_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={instance.certificate_file.name}'
        return response


class SubmitTestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        enrollment_id = request.data.get('test_enrollment_id')
        answers_data = request.data.get('answers', [])

        if not enrollment_id or not answers_data:
            return Response({'error': 'Test enrollment ID and answers are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            TestSubmissionService.submit_test(enrollment_id, request.user, answers_data)
        except (ValueError, NotFound, ValidationError) as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Test submitted successfully.'}, status=status.HTTP_200_OK)


class FeedbackListView(generics.ListAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer


class GiveFeedbackView(generics.CreateAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.context['request'] = request

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Feedback submitted successfully."}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StartTestEnrollmentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        test_id = request.query_params.get('test_id')

        if not test_id:
            return Response({'error': 'Test ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        test_enrollment = get_object_or_404(TestEnrollment, id=test_id, student=request.user)

        if not test_enrollment.started_at:
            test_enrollment.started_at = timezone.now()
            test_enrollment.save()

        serializer = TestEnrollmentDetailSerializer(test_enrollment)
        return Response(serializer.data, status=status.HTTP_200_OK)



class GenerateQuestionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        course_id = request.query_params.get('course_id')
        test_type = request.query_params.get('type')

        if not course_id or not test_type:
            return Response({'error': 'Course ID and test type are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            test_type = int(test_type)
            test_id = TestGenerationService.generate_test(request.user, course_id, test_type)
            return Response({'test_id': test_id}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class InitialTestResultView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        course_id = request.query_params.get('course_id')
        test_type = request.query_params.get('type', 1)  

        if not course_id:
            return Response({'error': 'Course ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            test_type = int(test_type)
            if test_type not in [1, 2]: 
                raise ValueError
        except ValueError:
            return Response({'error': 'Invalid test type. Must be 1 (Pre-course) or 2 (Post-course).'}, status=status.HTTP_400_BAD_REQUEST)

        enrollment = Enrollment.objects.filter(course_id=course_id, user=request.user).first()
        if not enrollment:
            return Response({'error': 'You are not enrolled in this course.'}, status=status.HTTP_403_FORBIDDEN)

        test_enrollment = TestEnrollment.objects.filter(
            student=request.user,
            course_id=course_id,
            type=test_type
        ).first()

        if not test_enrollment:
            return Response({'finished': False}, status=status.HTTP_200_OK)

        return Response({
            'finished': test_enrollment.finished,
            'test_results': TestEnrollmentSerializer(test_enrollment).data
        }, status=status.HTTP_200_OK)
