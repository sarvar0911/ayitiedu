from django.db import models
from django.conf import settings
from tinymce.models import HTMLField
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class Course(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(unique=True, blank=True)
    description = HTMLField()
    short_description = models.TextField()
    image = models.ImageField(upload_to='course_images/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    test_submission_count = models.IntegerField(default=0)
    test_question_count = models.IntegerField(default=0)
    test_duration = models.IntegerField(default=0)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='courses'
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def clean(self):
        if self.price < 0:
            raise ValidationError("Price cannot be negative.")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'


class Module(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules'
    )
    title = models.CharField(max_length=255)
    description = HTMLField(blank=True, null=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name = 'Module'
        verbose_name_plural = 'Modules'
        constraints = [
            models.UniqueConstraint(fields=['course', 'title'], name='unique_module_per_course')
        ]


class Lesson(TimestampedModel):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(max_length=255)
    description = HTMLField()
    pdf = models.FileField(
        upload_to='lessons_pdfs/', 
        blank=True, 
        null=True, 
        validators=[FileExtensionValidator(['pdf'])]
    )
    video_url = models.URLField(blank=True, null=True)
    presentation = models.FileField(
        upload_to='lessons_presentations/', 
        blank=True, 
        null=True, 
        validators=[FileExtensionValidator(['ppt', 'pptx', 'odp'])]
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name = 'Lesson'
        verbose_name_plural = 'Lessons'
        constraints = [
            models.UniqueConstraint(fields=['module', 'title'], name='unique_lesson_per_module')
        ]


class Enrollment(TimestampedModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        db_index=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        db_index=True
    )
    has_access = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    contract_file = models.FileField(blank=True, null=True, upload_to='course_files/')

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

    class Meta:
        verbose_name = 'Enrollment'
        verbose_name_plural = 'Enrollments'


class StudentCourseHistory(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='course_histories'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_histories'
    )
    total_score = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

    class Meta:
        verbose_name = 'Student Course History'
        verbose_name_plural = 'Student Course Histories'
        

class StudentLessonProgress(TimestampedModel):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        limit_choices_to={'role': 'student'},
        on_delete=models.CASCADE,
        related_name='lesson_progress'
    )
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        related_name='lesson_progress',
        db_index=True
    )
    lesson = models.ForeignKey(
        'Lesson',
        on_delete=models.CASCADE,
        related_name='student_progress'
    )
    
    def __str__(self):
        return f"{self.student.username} - {self.lesson.title}"

    class Meta:
        unique_together = ['student', 'lesson']
        verbose_name = 'Student Lesson Progress'
        verbose_name_plural = 'Student Lesson Progresses'


class ChatMessage(models.Model):
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='chat_messages'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_messages'
    )
    message = models.TextField()
    type = models.IntegerField(choices=((1, 'right'), (2, 'left')))
    date = models.DateTimeField(auto_now_add=True)
    reply = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='replies',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.module.title}"

    class Meta:
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
