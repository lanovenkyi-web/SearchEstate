# Импорты Django для работы с моделями и валидацией
from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError


# OopCompanion:suppressRename
USER_MODEL = get_user_model()




class Booking(models.Model):
    """
    Модель бронирования объекта недвижимости
    """
    # Варианты статусов бронирования
    STATUS_CHOICES = (
        ('new', 'Новое'),
        ('confirmed', 'Подтверждено'),
        ('rejected', 'Отклонено'),
        ('canceled', 'Отменено'),
    )

    # Связь с объектом недвижимости (объявлением)
    listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    # Арендатор (пользователь, который бронирует)
    tenant = models.ForeignKey(
        USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tenant_bookings'
    )
    # Дата начала аренды
    start_date = models.DateField()
    # Дата окончания аренды
    end_date = models.DateField()
    # Статус бронирования с выбором из предопределенных вариантов
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='new'
    )

    def clean(self):
        """
        Валидация данных перед сохранением
        """
        if self.end_date < self.start_date:
            raise ValidationError('Дата конца не может быть раньше даты начала')

    def __str__(self):
        """
        Строковое представление бронирования
        """
        return f"{self.listing} ({self.start_date} - {self.end_date})"