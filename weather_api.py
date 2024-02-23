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

    def get_location(self, city):
        # 使用Nominatim获取城市的经纬度
        location = self.geolocator.geocode(city)
        return location
    
    # response 分开处理？比如getCurrentTem
    def get_weather_data(self, city):
        # 获取地理位置信息
        location = self.get_location(city)

        params = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "current": "temperature_2m",
            "forecast_days": 1
        }

        weather_data = self.client.weather_api(OPENMETEO_ENDPOINT, params=params)
        return weather_data[0]

    def get_current_temperature_2m(self, city):
        current = self.get_weather_data(city).Current()
        current_temperature_2m = current.Variables(0).Value()
        return current_temperature_2m




""" # print(dir(response))
print(f"City Berlin")
print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation {response.Elevation()} m asl")
print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

print(f"Current time {current.Time()}")
print(f"Current temperature_2m {current_temperature_2m}") """
