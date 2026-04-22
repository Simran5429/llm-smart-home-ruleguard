import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from simulator.home_state import load_smart_home_state
from llm.generator import generate_rule
from validator.checker import validate_rule, check_intent_mismatch

# Load smart home state
data = load_smart_home_state()

# Example user input
while True:
    user_input = input("\nEnter your smart home command (type 'exit' to quit): ")

    if user_input.lower() == "exit":
        print("Exiting...")
        break

    print("User Input:", user_input)

    rule = generate_rule(user_input, data)

    print("Generated Rule:")
    print(rule)

    result = validate_rule(rule, data)

    print("\nValidation Result:")
    print(result)

    mismatch_result = check_intent_mismatch(user_input, rule)

    print("\nIntent Check Result:")
    print(mismatch_result)

