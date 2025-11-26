
from django.contrib import admin
from .models import WeatherRecord

@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    list_display=("city","date","temp_high","temp_low","precipitation","condition")
    list_filter=("city","condition","date")
    search_fields=("city",)
    ordering=("-date",)
