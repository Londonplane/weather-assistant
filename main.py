from api import get_completion, get_location, get_date, get_num_days
from weather_api import WeatherAPI

# user_prompt = input("Hi, what can I help you? \n")
user_prompt = "What's the weather like in Berlin for the next two days?"
completion = get_completion(user_prompt)
print(completion)

function_spec = completion.choices[0].message.tool_calls[0].function.name
weather_api = WeatherAPI()
if function_spec == "get_current_weather":
    location = get_location(completion)
    temperature, wind_speed = weather_api.get_current_weather(function_spec, location)
    print(temperature)
    print(wind_speed)
    
elif function_spec == "get_specific_day_weather":
    location = get_location(completion)
    date = get_date(completion)
    (
        temperature_max,
        temperature_min,
        wind_speed_max,
        precipitation_probability_mean,
        sunshine_duration,
    ) = weather_api.get_daily_weather(function_spec, location, date)
    print(temperature_max)
    print(temperature_min)
    print(wind_speed_max)
    print(precipitation_probability_mean)
    print(sunshine_duration / 3600)

elif function_spec == "get_n_day_weather":
    location = get_location(completion)
    date = get_date(completion)
    resolved_date = weather_api.resolve_relative_date(date)
    num_days = get_num_days(completion)

    weather_data_list = weather_api.get_num_days_weather(function_spec, location, resolved_date, num_days)
    for day_data in weather_data_list:
        print(day_data)