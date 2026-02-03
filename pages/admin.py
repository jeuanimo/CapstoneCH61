from django.contrib import admin
from .models import Event

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'location', 'image')
    list_filter = ('start_date', 'category')
    search_fields = ('title', 'description', 'location')
    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'category')
        }),
        ('Date & Time', {
            'fields': ('start_date', 'end_date')
        }),
        ('Location & Media', {
            'fields': ('location', 'image')
        }),
    )

admin.site.register(Event, EventAdmin)
