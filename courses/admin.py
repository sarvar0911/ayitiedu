from django.contrib import admin
from .models import (
    Course,
    Module,
    Lesson,
    Enrollment,
    StudentCourseHistory,
    StudentLessonProgress,
    ChatMessage,
)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'short_description', 'price', 'teacher')
    search_fields = ('title', 'short_description')
    list_filter = ('teacher', 'price')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'title', 'completed')
    search_fields = ('title',)
    list_filter = ('course', 'completed')
    ordering = ('-course', 'title')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'module', 'title', 'pdf', 'video_url', 'presentation')
    search_fields = ('title', 'module__title')
    list_filter = ('module',)
    ordering = ('-module', 'title')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'has_access', 'completed', 'started_date', 'completed_date')
    search_fields = ('user__username', 'course__title')
    list_filter = ('has_access', 'completed')
    ordering = ('-started_date',)


@admin.register(StudentCourseHistory)
class StudentCourseHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'total_score', 'completed')
    search_fields = ('user__username', 'course__title')
    list_filter = ('completed',)
    ordering = ('-completed',)


@admin.register(StudentLessonProgress)
class StudentLessonProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'lesson', 'course')
    search_fields = ('student__username', 'lesson__title', 'course__title')
    list_filter = ('course',)
    ordering = ('-student',)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'module', 'message', 'date', 'type')
    search_fields = ('user__username', 'message')
    list_filter = ('module', 'type', 'date')
    ordering = ('-date',)
