import json
from openai import OpenAI
client = OpenAI()
# 封装密钥？

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
          "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
        },
        "required": ["location"],
      },
    }
  }
]


def get_completion(msg):
  messages = [{"role": "user", "content": msg}]

  # tool 其实可以单独放一个地方
  completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages,
    tools=tools,
    tool_choice="auto"
  )
  return completion

def get_city(completion):
  arguments = completion.choices[0].message.tool_calls[0].function.arguments
  city = json.loads(arguments)["location"]
  return city