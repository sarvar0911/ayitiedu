from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Teacher, User


class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Role', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role'),
        }),
    )
    list_display = ('username', 'role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username',)
    ordering = ('username',)

admin.site.register(User, UserAdmin)
admin.site.register(Teacher)
