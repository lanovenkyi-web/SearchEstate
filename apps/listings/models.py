from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


# OopCompanion:suppressRename

USER_MODEL = get_user_model()

#======================================================================================================================

class Estate(models.Model):

    HOUSING_TYPES = [
        ('apartment', 'Квартира'),
        ('house', 'Дом'),
        ('studio', 'Студия'),
        ('room', 'Комната'),
    ]

    owner = models.ForeignKey(
        USER_MODEL,
        on_delete=models.CASCADE,
        related_name='estates',
        verbose_name="Владелец"
    )
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")


    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Цена"
    )
    rooms = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(50)],
        verbose_name="Комнат"
    )
    housing_type = models.CharField(
        max_length=50,
        choices=HOUSING_TYPES,
        verbose_name="Тип жилья"
    )
    city = models.CharField(max_length=100, verbose_name="Город")
    district = models.CharField(max_length=100, verbose_name="Район")

    class Meta:
        verbose_name = "Объект недвижимости"
        verbose_name_plural = "Объекты недвижимости"

    def __str__(self):
        return f"{self.title} ({self.city})"

#======================================================================================================================

class Listing(models.Model):


    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активно'
        BOOKED = 'booked', 'Забронировано'
        ARCHIVED = 'archived', 'Архивировано'

    estate = models.ForeignKey(
        Estate,
        on_delete=models.CASCADE,
        related_name='listings',
        verbose_name="Объект"
    )
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name="Статус"
    )


    views_count = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ['-created_at']

    def __str__(self):
        return f"Объявление: {self.estate.title} [{self.get_status_display()}]"

