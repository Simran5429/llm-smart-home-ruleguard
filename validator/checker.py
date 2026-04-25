def validate_rule(rule, smart_home_data):
    if rule is None:
        return {
            "valid": False,
            "reason": "Rule is None"
        }

    rooms = smart_home_data.get("rooms", {})

    # ---------- ACTION VALIDATION ----------
    action = rule.get("action", {})
    device_path = action.get("device", "")

    if "." not in device_path:
        return {
            "valid": False,
            "reason": "Invalid device format"
        }

    room_name, device_name = device_path.split(".")

    if room_name not in rooms:
        return {
            "valid": False,
            "reason": f"Room '{room_name}' does not exist"
        }

    devices = rooms[room_name].get("devices", {})
    if device_name not in devices:
        return {
            "valid": False,
            "reason": f"Device '{device_name}' does not exist in room '{room_name}'"
        }

    command = action.get("command", "")
    allowed_actions = devices[device_name].get("actions", [])

    if command not in allowed_actions:
        return {
            "valid": False,
            "reason": f"Command '{command}' is not supported by device '{device_name}'"
        }

    # ---------- TRIGGER VALIDATION ----------
    trigger = rule.get("trigger")

    if trigger:
        source = trigger.get("source", "")

        if "." not in source:
            return {
                "valid": False,
                "reason": "Invalid sensor format"
            }

        room_name, sensor_name = source.split(".")

        if room_name not in rooms:
            return {
                "valid": False,
                "reason": f"Room '{room_name}' does not exist (trigger)"
            }

        sensors = rooms[room_name].get("sensors", {})
        if sensor_name not in sensors:
            return {
                "valid": False,
                "reason": f"Sensor '{sensor_name}' does not exist in room '{room_name}'"
            }

    # ---------- FINAL ----------
    return {
        "valid": True,
        "reason": "Rule is valid"
    }

def check_intent_mismatch(user_input, rule):
    if rule is None:
        return {
            "mismatch": True,
            "reason": "No rule generated"
        }

    user_text = user_input.lower()
    generated_command = rule.get("action", {}).get("command", "").lower()
    generated_device = rule.get("action", {}).get("device", "").lower()

    if "light" in user_text and "temperature" in user_text:
        if "light" in generated_device and generated_command != "set_temperature":
            return {
                "mismatch": True,
                "reason": "User asked to set light temperature, but generated rule changed the intent"
            }

    if "kitchen" in user_text and "kitchen" not in generated_device:
        return {
            "mismatch": True,
            "reason": f"User asked for kitchen, but generated rule uses '{generated_device}'"
        }

    return {
        "mismatch": False,
        "reason": "No intent mismatch detected"
    }

def suggest_alternative(rule, smart_home_data):
    if rule is None:
        return None

    rooms = smart_home_data.get("rooms", {})
    action = rule.get("action", {})
    device_path = action.get("device", "")

    if "." not in device_path:
        return None

    requested_room, requested_device = device_path.split(".")

    suggestions = []

    for room_name, room_data in rooms.items():
        devices = room_data.get("devices", {})

        # If device exists in another room
        if requested_device in devices:
            suggestions.append(f"{room_name}.{requested_device}")

    if suggestions:
        return f"Did you mean: {suggestions[0]}?"

    # fallback: suggest any available device
    for room_name, room_data in rooms.items():
        devices = list(room_data.get("devices", {}).keys())
        if devices:
            return f"Available example: {room_name}.{devices[0]}"

    return None