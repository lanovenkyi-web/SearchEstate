from django.contrib import admin
from .models import Booking


# OopCompanion:suppressRename


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('listing', 'tenant', 'start_date', 'end_date', 'status')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('listing__estate__title', 'tenant__email', 'listing__estate__city')
    ordering = ('-start_date',)

    fieldsets = (
        ('Информация о бронировании', {
            'fields': ('listing', 'tenant', 'start_date', 'end_date', 'status')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('listing', 'listing__estate', 'tenant')

    def get_listing_title(self, obj):
        return obj.listing.estate.title

    get_listing_title.short_description = 'Объект'

    def get_tenant_email(self, obj):
        return obj.tenant.email

    get_tenant_email.short_description = 'Арендатор'
