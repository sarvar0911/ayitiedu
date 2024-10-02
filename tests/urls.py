from django.urls import path
from .views import (
    StudentResultsView,
    StudentResultsDetailView,
    SubmitTestView,
    FeedbackListView,
    GiveFeedbackView,
    StartTestEnrollmentView,
    GenerateQuestionsView,
    InitialTestResultView
)

urlpatterns = [
    path('results/', StudentResultsView.as_view(), name='student-results'),
    path('results/<int:pk>/', StudentResultsDetailView.as_view(), name='student-result-detail'),
    path('submit/', SubmitTestView.as_view(), name='submit-test'),
    path('feedbacks/', FeedbackListView.as_view(), name='feedback-list'),
    path('feedbacks/give/', GiveFeedbackView.as_view(), name='give-feedback'),
    path('test/start/', StartTestEnrollmentView.as_view(), name='start-test-enrollment'),
    path('test/generate/', GenerateQuestionsView.as_view(), name='generate-questions'),
    path('test/initial/', InitialTestResultView.as_view(), name='initial-test-result'),
]
