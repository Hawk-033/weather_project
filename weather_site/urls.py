
from django.contrib import admin
from django.urls import path
from weather.views import (
    dashboard,
    city_analytics,
    weather_comparison,
    weather_trends,
    user_achievements,
    api_weather_data,
    search_location
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('analytics/<str:city_name>/', city_analytics, name='city_analytics'),
    path('comparison/', weather_comparison, name='weather_comparison'),
    path('trends/', weather_trends, name='weather_trends'),
    path('achievements/', user_achievements, name='achievements'),
    path('api/weather/', api_weather_data, name='api_weather_data'),
    path('api/search/', search_location, name='search_location'),
]
