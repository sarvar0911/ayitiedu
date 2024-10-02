import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db import models
from django.utils import timezone


class CustomUserManager(UserManager):
    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    TEACHER = 'teacher'
    STUDENT = 'student'
    ADMIN = 'admin'

    ROLE_CHOICES = [
        (TEACHER, 'Teacher'),
        (STUDENT, 'Student'),
        (ADMIN, 'Admin'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True, default='')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STUDENT)

    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'name']

    def __str__(self):
        return f'{self.username} ({self.role})'


class Teacher(models.Model):
    fullname = models.CharField(max_length=150)
    speciality = models.CharField(max_length=100)
    picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self) -> str:
        return self.fullname
