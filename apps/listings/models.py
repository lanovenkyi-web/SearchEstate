# Импорты Django для работы с моделями и валидацией
from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


# OopCompanion:suppressRename
USER_MODEL = get_user_model()




class Listing(models.Model):
    """
    Модель объявления об аренде недвижимости
    """
    # Вложенный класс для определения статусов объявления
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активно'
        BOOKED = 'booked', 'Забронировано'
        ARCHIVED = 'archived', 'Архивировано'

    # Поле статуса объявления с выбором из предопределенных вариантов
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE
    )

    # Владелец объявления (пользователь)
    owner = models.ForeignKey(
        USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings'
    )
    # Заголовок объявления
    title = models.CharField(max_length=255)
    # Подробное описание объекта
    description = models.TextField()
    # Цена аренды
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[
            MinValueValidator(0)
        ]
    )
    # Количество комнат
    rooms = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(50)
        ]
    )
    # Тип жилья с выбором из предопределенных вариантов
    housing_type = models.CharField(
        max_length=50,
        choices=[
            ('apartment', 'Квартира'),
            ('house', 'Дом'),
            ('studio', 'Студия'),
            ('room', 'Комната'),
        ]
    )
    # Город расположения объекта
    city = models.CharField(max_length=100)
    # Район города
    district = models.CharField(max_length=100)
    # Флаг активности объявления
    is_active = models.BooleanField(default=True)
    # Счетчик просмотров объявления
    views_count = models.IntegerField(default=0)
    # Дата создания объявления (автоматически устанавливается)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Строковое представление объявления
        """
        return self.title

    class Meta:
        # Сортировка по дате создания (сначала новые)
        ordering = ['-created_at']