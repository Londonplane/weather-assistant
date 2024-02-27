import openmeteo_requests
import requests_cache
from retry_requests import retry
from geopy.geocoders import Nominatim
from config import CACHE_DIR, CACHE_EXPIRE_AFTER, RETRY_ATTEMPTS, RETRY_BACKOFF_FACTOR, OPENMETEO_ENDPOINT
from datetime import datetime, timedelta


class WeatherAPI:
    def __init__(self):
        # 初始化缓存会话和重试逻辑
        cache_session = requests_cache.CachedSession(
            CACHE_DIR, expire_after=CACHE_EXPIRE_AFTER)
        retry_session = retry(
            cache_session, retries=RETRY_ATTEMPTS, backoff_factor=RETRY_BACKOFF_FACTOR)

        # 初始化OpenMeteo API客户端
        self.client = openmeteo_requests.Client(session=retry_session)
        self.geolocator = Nominatim(user_agent="weather_assistant")

    @staticmethod
    def resolve_relative_date(relative_date):
        today = datetime.today()
        if relative_date == "today":
            date = today
        elif relative_date == "tomorrow":
            date = today + timedelta(days=1)
        elif relative_date == "day after tomorrow":
            date = today + timedelta(days=2)
        else:
            date = datetime.strptime(relative_date, "%Y-%m-%d")

        # 返回格式化的日期字符串
        return date.strftime("%Y-%m-%d")

    def get_weather_data(self, function_spec, location, date=None, num_days=None):
        # location.raw (all info for location)
        location_ = self.geolocator.geocode(location)

        params = {
            "latitude": location_.latitude,
            "longitude": location_.longitude,
        }

        # 根据forecast_type调整params字典
        if function_spec == 'get_current_weather':
            params["current"] = ["temperature_2m", "wind_speed_10m"]
        elif function_spec == 'get_specific_day_weather':
            resolved_date = WeatherAPI.resolve_relative_date(date)
            # print(resolved_date)
            params["start_date"] = resolved_date
            params["end_date"] = resolved_date
            params["daily"] = ["temperature_2m_max", "temperature_2m_min",
                               "precipitation_probability_mean", "wind_speed_10m_max"]

        elif function_spec == 'get_n_day_weather':
            params["forecast_days"] = num_days

        weather_data = self.client.weather_api(
            OPENMETEO_ENDPOINT, params=params)
        return weather_data[0]

    def get_current_weather(self, function_spec, location):
        current = self.get_weather_data(
            function_spec=function_spec, location=location).Current()

        current_temperature_2m = current.Variables(0).Value()
        current_wind_speed_10m = current.Variables(1).Value()

        return current_temperature_2m, current_wind_speed_10m

    def get_daily_weather(self, function_spec, location, date):
        daily = self.get_weather_data(function_spec, location, date).Daily()

        daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
        daily_precipitation_probability_mean = daily.Variables(
            2).ValuesAsNumpy()
        daily_wind_speed_10m_max = daily.Variables(3).ValuesAsNumpy()
        
        return daily_temperature_2m_max, daily_temperature_2m_min, daily_precipitation_probability_mean, daily_wind_speed_10m_max
