from django.conf import settings
from django.db import models
from django.core.validators import MaxValueValidator
from django.core.exceptions import ValidationError
from courses.models import Course
from datetime import datetime


class Feedback(models.Model):
    RATING_CHOICES = [(i, str(i)) for i in range(6)]
    
    full_name = models.CharField(max_length=200)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='feedbacks')
    feedback_text = models.TextField()
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=0, validators=[MaxValueValidator(5)])

    def clean(self):
        if Feedback.objects.filter(full_name=self.full_name, course=self.course).exists():
            raise ValidationError("You have already submitted feedback for this course.")
    
    def __str__(self):
        return f"{self.full_name} - {self.feedback_text[:50]}"

    class Meta:
        ordering = ['course', 'full_name']
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'


class TestQuestion(models.Model):
    TYPE_CHOICES = (
        (1, "Pre-course Test"),
        (2, "Post-course Test"),
    )
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='test_questions')
    question_text = models.TextField()
    question_type = models.IntegerField(choices=TYPE_CHOICES, default=1)
    image = models.ImageField(blank=True, null=True, upload_to='test_question_images/')

    def clean(self):
        if not self.question_text and not self.image:
            raise ValidationError("Either question text or image must be provided.")

    def __str__(self):
        return self.question_text[:50]

    class Meta:
        ordering = ['course', 'question_text']
        verbose_name = 'Test Question'
        verbose_name_plural = 'Test Questions'


class TestEnrollment(models.Model):
    TYPE_CHOICES = (
        (1, "Pre-course Test"),
        (2, "Post-course Test"),
    )
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, limit_choices_to={'role': 'student'}, on_delete=models.CASCADE, related_name='test_enrollments')
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    type = models.IntegerField(choices=TYPE_CHOICES, default=1)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    finished = models.BooleanField(default=False)
    questions = models.ManyToManyField('TestQuestion', related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='test_enrollments')
    certificate_file = models.FileField(blank=True, null=True, upload_to='course_certificate_files/')

    def clean(self):
        if self.finished and not self.started_at:
            raise ValidationError("Test cannot be marked as completed without being started.")
        
        if self.completed_at and self.started_at and self.completed_at < self.started_at:
            raise ValidationError("Completion time cannot be earlier than start time.")
        
        if self.certificate_file and not self.finished:
            raise ValidationError("Certificate cannot be generated before the test is completed.")
        
    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

    class Meta:
        unique_together = ('student', 'course', 'type')
        ordering = ['student', 'course']
        verbose_name = 'Test Enrollment'
        verbose_name_plural = 'Test Enrollments'


class TestAnswer(models.Model):
    answer = models.CharField(max_length=200)
    correct_answer = models.BooleanField(default=False)
    question = models.ForeignKey('TestQuestion', on_delete=models.CASCADE, related_name='answers')

    def __str__(self):
        return self.answer[:50]

    class Meta:
        ordering = ['question']
        verbose_name = 'Test Answer'
        verbose_name_plural = 'Test Answers'


class StudentAnswer(models.Model):
    answer = models.ForeignKey('TestAnswer', on_delete=models.CASCADE, related_name='student_answers')
    question = models.ForeignKey('TestQuestion', on_delete=models.CASCADE, related_name='student_answers')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, limit_choices_to={'role': 'student'}, on_delete=models.CASCADE, related_name='student_answers')
    test_enrollment = models.ForeignKey('TestEnrollment', on_delete=models.CASCADE, related_name='student_answers', null=True)

    def __str__(self):
        return f"{self.student.username} - {self.question.question_text[:50]}"

    class Meta:
        unique_together = ('student', 'question')
        ordering = ['student', 'question']
        verbose_name = 'Student Answer'
        verbose_name_plural = 'Student Answers'
