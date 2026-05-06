# Импорты Django для работы с моделями пользователей
from django.contrib.auth.models import AbstractUser
from django.db import models


# OopCompanion:suppressRename


class User(AbstractUser):
    """
    Расширенная модель пользователя системы
    """
    # Вложенный класс для определения ролей пользователей
    class Role(models.TextChoices):
        TENANT = 'tenant', 'Арендатор'
        LANDLORD = 'landlord', 'Арендодатель'

    # Email пользователя (уникальный)
    email = models.EmailField(unique=True)  # Сделаем email обязательным и уникальным
    # Роль пользователя в системе
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.TENANT)
    # Номер телефона (необязательное поле)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    # Краткая биография пользователя (необязательное поле)
    bio = models.TextField(max_length=500, blank=True)

    # Указываем, что email теперь используется для логина вместо username (опционально, но удобно)
    USERNAME_FIELD = 'email'
    # Обязательные поля при создании пользователя
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        """
        Строковое представление пользователя
        """
        return f"{self.email} ({self.role})"

    class Meta:
        # Сортировка по дате регистрации (сначала новые)
        ordering = ['-date_joined']