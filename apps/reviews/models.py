from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

USER_MODEL = get_user_model()
# OopCompanion:suppressRename

class Review(models.Model):

    listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    author = models.ForeignKey(
        USER_MODEL,
        on_delete=models.CASCADE,
        related_name='author_reviews'
    )
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review {self.rating} for {self.listing}"

    class Meta:
        ordering = ['-created_at']
