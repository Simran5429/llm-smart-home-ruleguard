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

Rules:
- Only use devices that exist
- Only use supported actions
- Output ONLY valid JSON (no explanation)

Format:
{{
  "trigger": {{
    "type": "sensor",
    "source": "room.sensor_name",
    "operator": "greater_than",
    "value": ""
  }},
  "action": {{
    "device": "room.device_name",
    "command": ""
  }}
}}

Important:
- The source field MUST use full format: room.sensor_name
- The device field MUST use full format: room.device_name
- Examples: bedroom.temperature_sensor, living_room.motion_sensor, bedroom.ac
- Do NOT output short names like ac or temperature_sensor
- Do NOT guess missing rooms or devices
- If the user's request mentions a room or device that does not exist, keep the original requested room/device wording in the JSON
- Output ONLY valid JSON

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
    except:
        print("⚠️ Failed to parse JSON, raw output:")
        print(output)
        return None