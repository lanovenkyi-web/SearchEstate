from django.contrib import admin
from .models import Estate, Listing


# OopCompanion:suppressRename


@admin.register(Estate)
class EstateAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'housing_type', 'city', 'price', 'rooms')
    list_filter = ('housing_type', 'city', 'rooms')
    search_fields = ('title', 'description', 'city', 'district')
    ordering = ('-created_at' if hasattr(Estate, 'created_at') else 'title',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('owner', 'title', 'description')
        }),
        ('Характеристики', {
            'fields': ('housing_type', 'rooms', 'price')
        }),
        ('Расположение', {
            'fields': ('city', 'district')
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner')


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('estate', 'status', 'views_count', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('estate__title', 'estate__description', 'estate__city')
    ordering = ('-created_at',)

    fieldsets = (
        ('Объявление', {
            'fields': ('estate', 'status')
        }),
        ('Статистика', {
            'fields': ('views_count',),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('views_count', 'created_at', 'updated_at')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('estate')
