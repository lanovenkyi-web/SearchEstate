from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


# OopCompanion:suppressRename


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'date_joined')
    search_fields = ('email', 'name', 'phone_number')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'name')}),
        ('Личная информация', {'fields': ('role', 'phone_number', 'bio')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'role'),
        }),
    )

    def get_role_display(self, obj):
        return obj.get_role_display()

    get_role_display.short_description = 'Роль'

    def save_model(self, request, obj, form, change):
        if not change:
            # При создании нового пользователя используем менеджер
            obj.set_password(form.cleaned_data['password1'])
        else:
            # При обновлении пароля
            if 'password1' in form.cleaned_data and form.cleaned_data['password1']:
                obj.set_password(form.cleaned_data['password1'])
        super().save_model(request, obj, form, change)
