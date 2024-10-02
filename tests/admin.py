from django.contrib import admin
from .models import Feedback, TestQuestion, TestEnrollment, TestAnswer, StudentAnswer


class TestAnswerInline(admin.TabularInline):
    model = TestAnswer
    extra = 1
    min_num = 1


class TestQuestionAdmin(admin.ModelAdmin):
    list_display = ['course', 'question_text', 'question_type']
    list_filter = ['course', 'question_type']
    search_fields = ['question_text']
    inlines = [TestAnswerInline]


class StudentAnswerInline(admin.TabularInline):
    model = StudentAnswer
    extra = 1


class TestEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'type', 'finished', 'started_at', 'completed_at']
    list_filter = ['course', 'type', 'finished']
    search_fields = ['student__username', 'course__title']
    inlines = [StudentAnswerInline]
    readonly_fields = ['certificate_file', 'total_questions', 'correct_answers', 'started_at', 'completed_at']

    def get_readonly_fields(self, request, obj=None):
        # Make 'finished' read-only after the test is completed
        if obj and obj.finished:
            return self.readonly_fields + ['finished']
        return self.readonly_fields


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'course', 'rating']
    list_filter = ['course', 'rating']
    search_fields = ['full_name', 'course__title']


admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(TestQuestion, TestQuestionAdmin)
admin.site.register(TestEnrollment, TestEnrollmentAdmin)
