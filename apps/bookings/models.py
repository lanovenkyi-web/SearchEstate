from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError


# OopCompanion:suppressRename
USER_MODEL = get_user_model()




class Booking(models.Model):

    STATUS_CHOICES = (
        ('new', 'Новое'),
        ('confirmed', 'Подтверждено'),
        ('rejected', 'Отклонено'),
        ('canceled', 'Отменено'),
    )

    listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    tenant = models.ForeignKey(
        USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tenant_bookings'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='new'
    )

    def clean(self):
        # Проверка, что дата окончания не раньше даты начала
        if self.end_date < self.start_date:
            raise ValidationError('End date cannot be earlier than start date')

    def __str__(self):
        return f"{self.listing} ({self.start_date} - {self.end_date})"