
from django.contrib import admin
from .models import WeatherRecord, UserWeatherPreference, UserAchievement, SearchHistory

@admin.register(WeatherRecord)
class WeatherRecordAdmin(admin.ModelAdmin):
    list_display = ("city", "date", "temp_high", "temp_low", "temp_avg", "precipitation", "humidity", "condition")
    list_filter = ("city", "condition", "date")
    search_fields = ("city",)
    ordering = ("-date",)
    readonly_fields = ("created_at", "temp_avg")
    fieldsets = (
        ('Location & Date', {
            'fields': ('city', 'date')
        }),
        ('Temperature', {
            'fields': ('temp_high', 'temp_low', 'temp_avg')
        }),
        ('Weather Details', {
            'fields': ('condition', 'precipitation', 'humidity', 'wind_speed')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserWeatherPreference)
class UserWeatherPreferenceAdmin(admin.ModelAdmin):
    list_display = ("user_id", "favorite_city", "unit_preference", "theme_preference", "updated_at")
    list_filter = ("unit_preference", "theme_preference", "updated_at")
    search_fields = ("user_id", "favorite_city")
    readonly_fields = ("created_at", "updated_at")


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ("user_id", "achievement_type", "points", "achieved_at")
    list_filter = ("achievement_type", "achieved_at", "points")
    search_fields = ("user_id", "achievement_type")
    readonly_fields = ("achieved_at",)
    ordering = ("-achieved_at",)


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ("location", "source", "found", "result_count", "searched_at")
    list_filter = ("source", "found", "searched_at")
    search_fields = ("location",)
    readonly_fields = ("searched_at",)
    ordering = ("-searched_at",)
