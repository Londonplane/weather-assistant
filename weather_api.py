import openmeteo_requests
import requests_cache
from retry_requests import retry
from geopy.geocoders import Nominatim
from config import (
    CACHE_DIR,
    CACHE_EXPIRE_AFTER,
    RETRY_ATTEMPTS,
    RETRY_BACKOFF_FACTOR,
    OPENMETEO_ENDPOINT,
)
from datetime import datetime, timedelta


class WeatherAPI:
    def __init__(self):
        # 初始化缓存会话和重试逻辑
        cache_session = requests_cache.CachedSession(
            CACHE_DIR, expire_after=CACHE_EXPIRE_AFTER
        )
        retry_session = retry(
            cache_session, retries=RETRY_ATTEMPTS, backoff_factor=RETRY_BACKOFF_FACTOR
        )

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
        if function_spec == "get_current_weather":
            params["current"] = ["temperature_2m", "wind_speed_10m"]
        elif function_spec == "get_specific_day_weather":
            params["start_date"] = WeatherAPI.resolve_relative_date(date)
            params["end_date"] = WeatherAPI.resolve_relative_date(date)
            params["daily"] = [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_probability_mean",
                "wind_speed_10m_max",
                "sunshine_duration",
            ]
        elif function_spec == "get_n_day_weather":
            params["forecast_days"] = num_days
            params["start_date"] = WeatherAPI.resolve_relative_date(date)
            # start_date = datetime.strptime(params["start_date"], "%Y-%m-%d")
            # end_date = start_date + timedelta(days=num_days - 1)
            # params["end_date"] = end_date.strftime("%Y-%m-%d")
            params["end_date"] = WeatherAPI.resolve_relative_date(date)
            params["daily"] = [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_probability_mean",
                "wind_speed_10m_max",
                "sunshine_duration",
            ]

        weather_data = self.client.weather_api(OPENMETEO_ENDPOINT, params=params)
        return weather_data[0]

    def get_current_weather(self, function_spec, location):
        current = self.get_weather_data(
            function_spec=function_spec, location=location
        ).Current()

        current_temperature_2m = current.Variables(0).Value()
        current_wind_speed_10m = current.Variables(1).Value()

        return current_temperature_2m, current_wind_speed_10m

    def get_daily_weather(self, function_spec, location, date):
        daily = self.get_weather_data(function_spec, location, date).Daily()

        daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
        daily_precipitation_probability_mean = daily.Variables(2).ValuesAsNumpy()
        daily_wind_speed_10m_max = daily.Variables(3).ValuesAsNumpy()
        daily_sunshine_duration = daily.Variables(4).ValuesAsNumpy()

        return (
            daily_temperature_2m_max,
            daily_temperature_2m_min,
            daily_precipitation_probability_mean,
            daily_wind_speed_10m_max,
            daily_sunshine_duration,
        )
    
    def get_num_days_weather(self, function_spec, location, start_date, num_days):
        weather_data_list = []  # 创建一个空列表来存储每天的天气数据

        # 循环num_days次，获取每天的天气数据
        for day in range(num_days):
            # 计算当前日期
            current_date = datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=day)
            # 将日期格式化为字符串，以便传递给get_daily_weather
            date_str = current_date.strftime("%Y-%m-%d")
            # 获取当天的天气数据
            daily_weather = self.get_daily_weather(function_spec, location, date_str)
            # 将当天的天气数据添加到列表中
            weather_data_list.append(daily_weather)

        return weather_data_list

