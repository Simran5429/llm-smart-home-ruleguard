from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_rule(user_input, smart_home_data):
    prompt = f"""
You are a smart home assistant.

Convert the user's request into a structured JSON rule.

Available smart home data:
{json.dumps(smart_home_data, indent=2)}

You must produce ONE of these two formats:

1. Direct command format (for simple commands like "turn on kitchen light"):
{{
  "action": {{
    "device": "room.device_name",
    "command": "supported_action"
  }}
}}

2. Automation rule format (for condition-based requests like "if bedroom temperature is above 27, turn on AC"):
{{
  "trigger": {{
    "type": "sensor",
    "source": "room.sensor_name",
    "operator": "greater_than",
    "value": 27
  }},
  "action": {{
    "device": "room.device_name",
    "command": "supported_action"
  }}
}}

Strict rules:
- Use only rooms, devices, sensors, and actions from the provided smart home data
- A trigger source MUST always be a sensor, never a device
- A device field MUST always be a device, never a sensor
- For simple direct user commands, return ONLY the action object
- For condition-based requests, return both trigger and action
- Do NOT add explanations
- Output ONLY valid JSON
- Do NOT guess missing rooms or devices
- If the user mentions a room or device that does not exist, preserve the requested wording in the JSON so the validator can catch it

Examples:
User: Turn on kitchen light
Output:
{{
  "action": {{
    "device": "kitchen.light",
    "command": "turn_on"
  }}
}}

User: If bedroom temperature is above 27, turn on AC
Output:
{{
  "trigger": {{
    "type": "sensor",
    "source": "bedroom.temperature_sensor",
    "operator": "greater_than",
    "value": 27
  }},
  "action": {{
    "device": "bedroom.ac",
    "command": "turn_on"
  }}
}}

User request:
{user_input}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{"role": "user", "content": prompt}]
    )

    output = response.choices[0].message.content.strip()

    if output.startswith("```json"):
        output = output.replace("```json", "", 1).strip()

    if output.startswith("```"):
        output = output.replace("```", "", 1).strip()

    if output.endswith("```"):
        output = output[:-3].strip()

    try:
        return json.loads(output)
    except Exception:
        print(" Failed to parse JSON, raw output:")
        print(output)
        return None