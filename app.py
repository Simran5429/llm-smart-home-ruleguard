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
user_input = "Set the bedroom light temperature to 20"
print("User Input:", user_input)

# Generate rule
rule = generate_rule(user_input, data)

print("Generated Rule:")
print(rule)

# Validate rule
result = validate_rule(rule, data)

print("\nValidation Result:")
print(result)

mismatch_result = check_intent_mismatch(user_input, rule)

print("\nIntent Check Result:")
print(mismatch_result)

