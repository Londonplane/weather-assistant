from api import get_completion, get_city
from weather_api import WeatherAPI



# 接收命令行输入
# user_prompt = input("Hi, what can I help you?")
user_prompt = "What's the weather like in Berlin today?"
print(user_prompt)
completion = get_completion(user_prompt);
city = get_city(completion);
print(f"City: {city}")

weather_api = WeatherAPI()
temperature = weather_api.get_current_temperature_2m(city)

print(temperature)


