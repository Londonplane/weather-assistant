import openmeteo_requests
import requests_cache
from retry_requests import retry
from geopy.geocoders import Nominatim
from config import CACHE_DIR, CACHE_EXPIRE_AFTER, RETRY_ATTEMPTS, RETRY_BACKOFF_FACTOR, OPENMETEO_ENDPOINT

class WeatherAPI:
    def __init__(self):
        # 初始化缓存会话和重试逻辑
        cache_session = requests_cache.CachedSession(CACHE_DIR, expire_after=CACHE_EXPIRE_AFTER)
        retry_session = retry(cache_session, retries=RETRY_ATTEMPTS, backoff_factor=RETRY_BACKOFF_FACTOR)
        
        # 初始化OpenMeteo API客户端
        self.client = openmeteo_requests.Client(session=retry_session)
        self.geolocator = Nominatim(user_agent="weather_assistant")
    
    def get_weather_data(self, city, forecast_type="current"):
        # location.raw (all info for location) 
        location = self.geolocator.geocode(city) 

        params = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "forecast_days": 1
        }

        # 根据forecast_type调整params字典
        if forecast_type == "current":
            params["current"] = ["temperature_2m", "wind_speed_10m"]
        elif forecast_type == "daily":
            params["daily"] = ["temperature_2m_max", "temperature_2m_min", "precipitation_probability_mean", "wind_speed_10m_max"]
        else:
            raise ValueError("Invalid forecast_type. Expected 'current' or 'daily'.")

        weather_data = self.client.weather_api(OPENMETEO_ENDPOINT, params=params)
        return weather_data[0]



    def get_current_weather(self, city):
        current = self.get_weather_data(city).Current()
        
        current_temperature_2m = current.Variables(0).Value()
        current_wind_speed_10m = current.Variables(1).Value()
        
        return current_temperature_2m,current_wind_speed_10m
    
    def get_daily_weather(self, city):
        daily = self.get_weather_data(city).Daily()
        
        daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy
        daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy
        daily_precipitation_probability_mean = daily.Variables(2).ValuesAsNumpy()
        daily_wind_speed_10m_max = daily.Variables(3).ValuesAsNumpy()

        return daily_temperature_2m_max,daily_temperature_2m_min,daily_precipitation_probability_mean,daily_wind_speed_10m_max
        


