from django.core.management.base import BaseCommand
from django.utils import timezone
from weather.models import WeatherRecord
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Populate database with sample weather data for popular global locations'

    def handle(self, *args, **options):
        # Popular global locations
        locations = [
            ('New York', 'USA'),
            ('London', 'UK'),
            ('Tokyo', 'Japan'),
            ('Paris', 'France'),
            ('Sydney', 'Australia'),
            ('Dubai', 'UAE'),
            ('Singapore', 'Singapore'),
            ('Toronto', 'Canada'),
            ('Mumbai', 'India'),
            ('Mexico City', 'Mexico'),
            ('Berlin', 'Germany'),
            ('Barcelona', 'Spain'),
            ('Bangkok', 'Thailand'),
            ('Istanbul', 'Turkey'),
            ('São Paulo', 'Brazil'),
        ]

        conditions = ['sunny', 'cloudy', 'rainy', 'snowy', 'stormy', 'foggy']
        
        created_count = 0
        
        for city, country in locations:
            # Create 30 days of weather data for each city
            for days_ago in range(30):
                date = (datetime.now().date() - timedelta(days=days_ago))
                
                # Generate realistic temperature variations
                base_temp = random.uniform(5, 30)
                temp_high = base_temp + random.uniform(5, 15)
                temp_low = base_temp - random.uniform(2, 8)
                temp_avg = (temp_high + temp_low) / 2
                
                # Generate other weather parameters
                precipitation = random.uniform(0, 25) if random.random() > 0.7 else 0
                humidity = random.randint(30, 90)
                wind_speed = random.uniform(0, 50)
                condition = random.choice(conditions)
                
                # Create or update the record
                record, created = WeatherRecord.objects.get_or_create(
                    city=city,
                    date=date,
                    defaults={
                        'temp_high': round(temp_high, 1),
                        'temp_low': round(temp_low, 1),
                        'temp_avg': round(temp_avg, 1),
                        'precipitation': round(precipitation, 1),
                        'humidity': humidity,
                        'wind_speed': round(wind_speed, 1),
                        'condition': condition,
                    }
                )
                
                if created:
                    created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} weather records for {len(locations)} popular locations'
            )
        )
