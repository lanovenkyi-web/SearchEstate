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
        ('Personal information', {'fields': ('role', 'phone_number', 'bio')}),
        ('Access rights', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'role'),
        }),
    )

    def get_role_display(self, obj):
        return obj.get_role_display()

    get_role_display.short_description = 'Role'

    def save_model(self, request, obj, form, change):
        if not change:
            # When creating a new user, use the manager
            obj.set_password(form.cleaned_data['password1'])
        else:
            # When updating password
            if 'password1' in form.cleaned_data and form.cleaned_data['password1']:
                obj.set_password(form.cleaned_data['password1'])
        super().save_model(request, obj, form, change)
