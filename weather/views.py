
from django.shortcuts import render
from django.db.models import Avg, Max, Min, Count, Q
from django.http import JsonResponse
from .models import WeatherRecord, UserAchievement, SearchHistory
from datetime import datetime, timedelta
import json
import requests

def dashboard(request):
    """Main dashboard with recent weather data and analytics"""
    records = WeatherRecord.objects.all()[:30]
    
    # Get unique cities
    cities = WeatherRecord.objects.values_list('city', flat=True).distinct()
    
    # Get latest records by city
    latest_records = []
    for city in cities:
        latest = WeatherRecord.objects.filter(city=city).latest('date')
        latest_records.append(latest)
    
    context = {
        'records': records,
        'latest_records': latest_records,
        'total_records': WeatherRecord.objects.count(),
        'cities_count': len(cities),
    }
    return render(request, 'dashboard.html', context)


def city_analytics(request, city_name):
    """Detailed analytics for a specific city"""
    city_records = WeatherRecord.objects.filter(city=city_name).order_by('-date')
    
    # Calculate statistics for the last 30 days
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_records = city_records.filter(date__gte=thirty_days_ago)
    
    stats = recent_records.aggregate(
        avg_temp=Avg('temp_avg'),
        max_temp=Max('temp_high'),
        min_temp=Min('temp_low'),
        total_precipitation=Avg('precipitation'),
        avg_humidity=Avg('humidity'),
        avg_wind=Avg('wind_speed'),
        record_count=Count('id')
    )
    
    context = {
        'city': city_name,
        'records': city_records[:30],
        'stats': stats,
        'chart_data': generate_chart_data(city_records[:30])
    }
    return render(request, 'analytics.html', context)


def weather_comparison(request):
    """Compare weather across multiple cities"""
    cities = WeatherRecord.objects.values_list('city', flat=True).distinct()
    
    comparison_data = {}
    for city in cities:
        latest = WeatherRecord.objects.filter(city=city).latest('date')
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        recent_stats = WeatherRecord.objects.filter(
            city=city,
            date__gte=thirty_days_ago
        ).aggregate(
            avg_temp=Avg('temp_avg'),
            max_temp=Max('temp_high'),
            min_temp=Min('temp_low'),
            total_precipitation=Avg('precipitation')
        )
        comparison_data[city] = {
            'latest': latest,
            'stats': recent_stats
        }
    
    context = {
        'comparison_data': comparison_data,
        'cities': list(cities)
    }
    return render(request, 'comparison.html', context)


def weather_trends(request):
    """Display weather trends and forecasts"""
    # Get all records from last 60 days grouped by city
    sixty_days_ago = datetime.now().date() - timedelta(days=60)
    records = WeatherRecord.objects.filter(date__gte=sixty_days_ago).order_by('city', 'date')
    
    # Group by city
    trends = {}
    for record in records:
        if record.city not in trends:
            trends[record.city] = []
        trends[record.city].append(record)
    
    context = {
        'trends': trends,
        'chart_data': generate_trend_chart_data(records)
    }
    return render(request, 'trends.html', context)


def user_achievements(request, user_id=1):
    """Display user achievements and gamification stats"""
    achievements = UserAchievement.objects.filter(user_id=user_id).order_by('-achieved_at')
    total_points = sum(a.points for a in achievements)
    
    context = {
        'user_id': user_id,
        'achievements': achievements,
        'total_points': total_points,
        'achievements_count': achievements.count(),
        'next_milestone': calculate_next_milestone(total_points)
    }
    return render(request, 'achievements.html', context)


def api_weather_data(request):
    """API endpoint for weather data"""
    city = request.GET.get('city', None)
    days = int(request.GET.get('days', 30))
    
    query = WeatherRecord.objects.all()
    if city:
        query = query.filter(city=city)
    
    records = query.order_by('-date')[:days]
    
    data = [{
        'city': r.city,
        'date': r.date.isoformat(),
        'temp_high': r.temp_high,
        'temp_low': r.temp_low,
        'temp_avg': r.temp_avg,
        'precipitation': r.precipitation,
        'humidity': r.humidity,
        'wind_speed': r.wind_speed,
        'condition': r.condition,
    } for r in records]
    
    return JsonResponse({'records': data})


def generate_chart_data(records):
    """Generate data for charts"""
    dates = []
    temps_high = []
    temps_low = []
    temps_avg = []
    
    for record in reversed(records):
        dates.append(str(record.date))
        temps_high.append(record.temp_high)
        temps_low.append(record.temp_low)
        temps_avg.append(record.temp_avg or 0)
    
    return {
        'dates': dates,
        'temps_high': temps_high,
        'temps_low': temps_low,
        'temps_avg': temps_avg,
    }


def generate_trend_chart_data(records):
    """Generate trend data for visualization"""
    by_city = {}
    for record in records:
        if record.city not in by_city:
            by_city[record.city] = {'dates': [], 'temps': []}
        by_city[record.city]['dates'].append(str(record.date))
        by_city[record.city]['temps'].append(record.temp_avg or 0)
    
    return by_city


def calculate_next_milestone(current_points):
    """Calculate next achievement milestone"""
    milestones = [50, 100, 250, 500, 1000]
    for milestone in milestones:
        if current_points < milestone:
            return {'points': milestone, 'remaining': milestone - current_points}
    return {'points': 1500, 'remaining': 1500 - current_points}


def search_location(request):
    """Search for weather data by location - checks database first, then OpenWeather API"""
    location = request.GET.get('location', '').strip()
    
    if not location:
        return JsonResponse({'error': 'Location parameter is required'}, status=400)
    
    # First, try to find in database
    db_records = WeatherRecord.objects.filter(
        city__iexact=location
    ).order_by('-date')[:7]
    
    if db_records.exists():
        # Found in database - save to search history
        SearchHistory.objects.create(
            location=location,
            source='database',
            result_count=len(db_records),
            found=True
        )
        
        # Found in database
        data = {
            'source': 'database',
            'location': location,
            'records': [{
                'city': r.city,
                'date': r.date.isoformat(),
                'temp_high': r.temp_high,
                'temp_low': r.temp_low,
                'temp_avg': r.temp_avg,
                'precipitation': r.precipitation,
                'humidity': r.humidity,
                'wind_speed': r.wind_speed,
                'condition': r.get_condition_display(),
            } for r in db_records]
        }
        return JsonResponse(data)
    
    # Not in database, try OpenWeather API
    try:
        # You need to set your OpenWeather API key
        api_key = 'b9886e11e1a6240e380cfa855fafc9da'  # Replace with actual API key
        
        # Get current weather
        url = f'https://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric'
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            weather_data = response.json()
            
            # Save successful API search to history
            SearchHistory.objects.create(
                location=location,
                source='api',
                result_count=1,
                found=True
            )
            
            # Format the response
            data = {
                'source': 'openweather_api',
                'location': weather_data.get('name', location),
                'current': {
                    'temp': weather_data['main']['temp'],
                    'temp_high': weather_data['main']['temp_max'],
                    'temp_low': weather_data['main']['temp_min'],
                    'humidity': weather_data['main']['humidity'],
                    'wind_speed': weather_data.get('wind', {}).get('speed', None),
                    'condition': weather_data['weather'][0]['main'],
                    'description': weather_data['weather'][0]['description'],
                }
            }
            return JsonResponse(data)
        else:
            # Save failed search to history
            SearchHistory.objects.create(
                location=location,
                source='api',
                result_count=0,
                found=False
            )
            return JsonResponse({'error': f'Location not found: {location}'}, status=404)
    
    except requests.exceptions.RequestException as e:
        # Save failed API request to history
        SearchHistory.objects.create(
            location=location,
            source='api',
            result_count=0,
            found=False
        )
        return JsonResponse({'error': f'API request failed: {str(e)}'}, status=500)
    except Exception as e:
        # Save unexpected error to history
        SearchHistory.objects.create(
            location=location,
            source='api',
            result_count=0,
            found=False
        )
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
