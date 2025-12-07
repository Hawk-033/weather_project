
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class WeatherRecord(models.Model):
    CONDITION_CHOICES = [
        ('sunny', 'Sunny'),
        ('cloudy', 'Cloudy'),
        ('rainy', 'Rainy'),
        ('snowy', 'Snowy'),
        ('stormy', 'Stormy'),
        ('foggy', 'Foggy'),
    ]
    
    city = models.CharField(max_length=100, db_index=True)
    date = models.DateField(db_index=True)
    temp_high = models.FloatField()
    temp_low = models.FloatField()
    temp_avg = models.FloatField(null=True, blank=True)
    precipitation = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    humidity = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    wind_speed = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0)])
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['city', 'date']
        indexes = [
            models.Index(fields=['city', '-date']),
            models.Index(fields=['-date']),
        ]

    def __str__(self):
        return f"{self.city} - {self.date}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate average temperature
        if not self.temp_avg:
            self.temp_avg = (self.temp_high + self.temp_low) / 2
        super().save(*args, **kwargs)


class UserWeatherPreference(models.Model):
    user_id = models.IntegerField(unique=True)  # Can be extended with User model
    favorite_city = models.CharField(max_length=100)
    theme_preference = models.CharField(
        max_length=20,
        choices=[('light', 'Light'), ('dark', 'Dark')],
        default='light'
    )
    unit_preference = models.CharField(
        max_length=10,
        choices=[('celsius', 'Celsius'), ('fahrenheit', 'Fahrenheit')],
        default='celsius'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for user {self.user_id}"


class UserAchievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('weather_watcher', 'Weather Watcher'),
        ('data_collector', 'Data Collector'),
        ('trend_analyst', 'Trend Analyst'),
        ('explorer', 'Explorer'),
    ]
    
    user_id = models.IntegerField()
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    description = models.TextField()
    points = models.IntegerField(default=10)
    achieved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user_id', 'achievement_type']

    def __str__(self):
        return f"Achievement: {self.achievement_type} for user {self.user_id}"


class SearchHistory(models.Model):
    location = models.CharField(max_length=100, db_index=True)
    source = models.CharField(
        max_length=20,
        choices=[('database', 'Database'), ('api', 'OpenWeather API')],
    )
    searched_at = models.DateTimeField(auto_now_add=True, db_index=True)
    result_count = models.IntegerField(default=0)
    found = models.BooleanField(default=True)

    class Meta:
        ordering = ['-searched_at']
        indexes = [
            models.Index(fields=['location', '-searched_at']),
            models.Index(fields=['-searched_at']),
        ]

    def __str__(self):
        return f"Search: {self.location} ({self.source}) - {self.searched_at}"
