from api import get_completion, get_location, get_date, get_num_days
from weather_api import WeatherAPI

# 接收命令行输入
# user_prompt = input("Hi, what can I help you? \n")
user_prompt = "What's the weather like in Berlin over the next three days?"
completion = get_completion(user_prompt)

function_spec = completion.choices[0].message.tool_calls[0].function.name
if function_spec == 'get_current_weather':
    location = get_location
elif function_spec == 'get_specific_day_weather':
    location = get_location
    data = get_date # format
elif function_spec == 'get_n_day_weather':
    location = get_location
    num_day = get_num_days

weather_api = WeatherAPI()

current_temperature, wind_speed = weather_api.get_current_weather(location)
print(current_temperature)
print(wind_speed)

