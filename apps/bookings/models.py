from django.contrib.auth import get_user_model
from django.db import models
from django.core.exceptions import ValidationError

# OopCompanion:suppressRename
USER_MODEL = get_user_model()


class Booking(models.Model):
    """Real estate booking model.
    
    Links a tenant with a listing for a specific period.
    Supports statuses: new, confirmed, rejected, canceled.
    """
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
        """Validates the booking.
        
        Checks that the end date is after the start date
        and that dates do not overlap with existing bookings.
        
        Raises:
            ValidationError: If dates are invalid or overlap
        """
        if self.end_date < self.start_date:
            raise ValidationError('Дата окончания не может быть раньше даты начала')

        if self.listing_id:
            overlapping_bookings = Booking.objects.filter(
                listing=self.listing,
                status__in=['new', 'confirmed'],
                start_date__lte=self.end_date,
                end_date__gte=self.start_date
            ).exclude(pk=self.pk)

            if overlapping_bookings.exists():
                raise ValidationError('Даты бронирования пересекаются с существующим бронированием')

    def save(self, *args, **kwargs):
        # Saves the booking with validation.

        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.listing} ({self.start_date} - {self.end_date})"
