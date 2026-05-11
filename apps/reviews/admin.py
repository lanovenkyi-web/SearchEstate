from django.contrib import admin
from .models import Review


# OopCompanion:suppressRename


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('listing', 'author', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('listing__estate__title', 'author__email', 'text')
    ordering = ('-created_at',)

    fieldsets = (
        ('Отзыв', {
            'fields': ('listing', 'author', 'rating', 'text')
        }),
    )

    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('listing', 'listing__estate', 'author')

    def get_listing_title(self, obj):
        return obj.listing.estate.title

    get_listing_title.short_description = 'Объект'

    def get_author_email(self, obj):
        return obj.author.email

    get_author_email.short_description = 'Автор'
