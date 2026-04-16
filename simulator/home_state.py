import json

def load_smart_home_state():
    with open("data/smart_home.json", "r") as file:
        data = json.load(file)
    return data