
from django.db import models

class WeatherRecord(models.Model):
    city=models.CharField(max_length=100)
    date=models.DateField()
    temp_high=models.FloatField()
    temp_low=models.FloatField()
    precipitation=models.FloatField(null=True, blank=True)
    condition=models.CharField(max_length=50)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering=['-date']

    def __str__(self):
        return f"{self.city} - {self.date}"
