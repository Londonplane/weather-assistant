from api import get_completion, get_location, get_date, get_num_days
from weather_api import WeatherAPI

# 接收命令行输入
# user_prompt = input("Hi, what can I help you? \n")
user_prompt = "How is the weather in Berlin tomorrow?"
completion = get_completion(user_prompt)

function_spec = completion.choices[0].message.tool_calls[0].function.name
weather_api = WeatherAPI()
if function_spec == 'get_current_weather':
    location = get_location(completion)
    temperature, wind_speed = weather_api.get_current_weather(
        function_spec, location)
    print(temperature)
    print(wind_speed)
elif function_spec == 'get_specific_day_weather':
    location = get_location(completion)
    date = get_date(completion)
    temperature_max, temperature_min, wind_speed_max, precipitation_probability_mean = weather_api.get_daily_weather(
        function_spec, location, date)
    print(temperature_max)
    print(temperature_min)
    print(wind_speed_max)
    print(precipitation_probability_mean)

elif function_spec == 'get_n_day_weather':
    location = get_location(completion)
    num_days = get_num_days(completion)
