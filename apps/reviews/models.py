# Импортируем модель пользователя из Django
from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Получаем модель пользователя
USER_MODEL = get_user_model()
# OopCompanion:suppressRename

class Review(models.Model):
    """
    Модель отзыва на объект недвижимости
    """
    # Связь с объектом недвижимости (объявлением)
    listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    # Автор отзыва (пользователь)
    author = models.ForeignKey(
        USER_MODEL,
        on_delete=models.CASCADE,
        related_name='author_reviews'
    )
    # Рейтинг отзыва (от 1 до 5)
    rating = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    # Текст отзыва
    text = models.TextField()
    # Дата создания отзыва (автоматически устанавливается)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Строковое представление отзыва
        """
        return f"Review {self.rating} for {self.listing}"

    class Meta:
        # Сортировка по дате создания (сначала новые)
        ordering = ['-created_at']