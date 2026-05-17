from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


# OopCompanion:suppressRename


class UserManager(BaseUserManager):
    """Manager for user management."""

    def create_user(self, email, password=None, role='tenant', **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """User model with custom authentication system.
    
    Uses email as the primary field for login.
    Supports three roles: administrator, landlord, tenant.
    """

    class Role(models.TextChoices):
        """Варианты ролей пользователя."""
        ADMIN = 'admin', 'Администратор'
        LANDLORD = 'landlord', 'Арендодатель'
        TENANT = 'tenant', 'Арендатор'

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.TENANT)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_landlord(self):
        return self.role == self.Role.LANDLORD

    def is_tenant(self):
        return self.role == self.Role.TENANT

    class Meta:
        ordering = ['-date_joined']
