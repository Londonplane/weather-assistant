import json
from openai import OpenAI

client = OpenAI()

# date: Year默认2024，Month,Day需要强制User正确输入, like "tomorrow" 在调用weather_api处理
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_specific_day_weather",
            "description": "Get the weather forecast for a specific or relative day.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g., San Francisco, CA.",
                    },
                    "date": {
                        "type": "string",
                        "description": "The specific date for the weather forecast, in YYYY-MM-DD format, or a relative day such as 'today', 'tomorrow', or 'day after tomorrow'. By default, the year is set to 2024.",
                    },
                },
                "required": ["location", "date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_n_day_weather",
            "description": "Get an N-day weather forecast for a specified location. The forecast can start from a specific date, a relative day, or a date without a year specified, in which case the year 2024 is assumed. If no start date is specified, the forecast starts from today.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g., San Francisco, CA.",
                    },
                    "date": {
                        "type": "string",
                        "description": "The start date for the weather forecast. This can be in YYYY-MM-DD format, a relative day such as 'today', 'tomorrow', or 'day after tomorrow', or a date without the year specified, in which case the year 2024 is assumed. If not specified, defaults to 'today'.",
                    },
                    "num_days": {
                        "type": "integer",
                        "description": "The number of days to forecast, starting from the 'start_date'. The forecast includes the start date.",
                    },
                },
                "required": ["location", "date", "num_days"],
            },
        },
    },
]


def get_completion(msg):
    messages = [{"role": "user", "content": msg}]

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages, tools=tools, tool_choice="auto"
    )
    return completion


def get_location(completion):
    arguments = completion.choices[0].message.tool_calls[0].function.arguments
    location = json.loads(arguments)["location"]
    return location


def get_date(completion):
    arguments = completion.choices[0].message.tool_calls[0].function.arguments
    date = json.loads(arguments)["date"]
    return date


def get_num_days(completion):
    arguments = completion.choices[0].message.tool_calls[0].function.arguments
    num_days = json.loads(arguments)["num_days"]
    return num_days
