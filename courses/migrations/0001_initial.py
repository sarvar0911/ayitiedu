# Generated by Django 5.1.1 on 2024-09-25 09:46

import django.core.validators
import django.db.models.deletion
import tinymce.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(db_index=True, max_length=255)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('description', tinymce.models.HTMLField()),
                ('short_description', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='course_images/')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('test_submission_count', models.IntegerField(default=0)),
                ('test_question_count', models.IntegerField(default=0)),
                ('test_duration', models.IntegerField(default=0)),
                ('teacher', models.ForeignKey(limit_choices_to={'role': 'teacher'}, on_delete=django.db.models.deletion.CASCADE, related_name='courses', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Course',
                'verbose_name_plural': 'Courses',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('started_date', models.DateTimeField(blank=True, null=True)),
                ('completed_date', models.DateTimeField(blank=True, null=True)),
                ('has_access', models.BooleanField(default=False)),
                ('completed', models.BooleanField(default=False)),
                ('contract_file', models.FileField(blank=True, null=True, upload_to='course_files/')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to='courses.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='enrollments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Enrollment',
                'verbose_name_plural': 'Enrollments',
            },
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', tinymce.models.HTMLField(blank=True, null=True)),
                ('completed', models.BooleanField(default=False)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modules', to='courses.course')),
            ],
            options={
                'verbose_name': 'Module',
                'verbose_name_plural': 'Modules',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('started_date', models.DateTimeField(blank=True, null=True)),
                ('completed_date', models.DateTimeField(blank=True, null=True)),
                ('title', models.CharField(max_length=255)),
                ('description', tinymce.models.HTMLField()),
                ('pdf', models.FileField(blank=True, null=True, upload_to='lessons_pdfs/', validators=[django.core.validators.FileExtensionValidator(['pdf'])])),
                ('video_url', models.URLField(blank=True, null=True)),
                ('presentation', models.FileField(blank=True, null=True, upload_to='lessons_presentations/', validators=[django.core.validators.FileExtensionValidator(['ppt', 'pptx', 'odp'])])),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lessons', to='courses.module')),
            ],
            options={
                'verbose_name': 'Lesson',
                'verbose_name_plural': 'Lessons',
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('type', models.IntegerField(choices=[(1, 'right'), (2, 'left')])),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('reply', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to='courses.chatmessage')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_messages', to=settings.AUTH_USER_MODEL)),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat_messages', to='courses.module')),
            ],
            options={
                'verbose_name': 'Chat Message',
                'verbose_name_plural': 'Chat Messages',
            },
        ),
        migrations.CreateModel(
            name='StudentCourseHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_score', models.PositiveIntegerField(default=0)),
                ('completed', models.BooleanField(default=False)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_histories', to='courses.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='course_histories', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Student Course History',
                'verbose_name_plural': 'Student Course Histories',
            },
        ),
        migrations.CreateModel(
            name='StudentLessonProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson_progress', to='courses.course')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_progress', to='courses.lesson')),
                ('student', models.ForeignKey(limit_choices_to={'role': 'student'}, on_delete=django.db.models.deletion.CASCADE, related_name='lesson_progress', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Student Lesson Progress',
                'verbose_name_plural': 'Student Lesson Progresses',
            },
        ),
        migrations.AddConstraint(
            model_name='module',
            constraint=models.UniqueConstraint(fields=('course', 'title'), name='unique_module_per_course'),
        ),
        migrations.AddConstraint(
            model_name='lesson',
            constraint=models.UniqueConstraint(fields=('module', 'title'), name='unique_lesson_per_module'),
        ),
        migrations.AlterUniqueTogether(
            name='studentlessonprogress',
            unique_together={('student', 'lesson')},
        ),
    ]
