# RuleGuard: Enhancing Reliability in LLM-Based Smart Home Systems

RuleGuard is a prototype smart home automation system that uses a Large Language Model (LLM) to convert natural language commands into structured automation rules. The project focuses on improving reliability by detecting hallucinations and intent mismatches before rule execution.

## Project Goal

The goal of this project is to make LLM-based smart home systems more reliable by grounding generated rules in actual smart home context and validating them before execution.

## What the system does so far

- Loads a simulated smart home environment from JSON
- Uses GPT to convert user commands into structured automation rules
- Validates generated rules against available rooms, devices, sensors, and supported actions
- Detects some intent mismatches when the generated rule changes the user's original meaning

## Current Project Structure

```

llm-smart-home-ruleguard/
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
│
├── data/
│   └── smart_home.json
│
├── llm/
│   └── generator.py
│
├── simulator/
│   └── home_state.py
│
└── validator/
    └── checker.py

```


## Example Workflow
- User gives a natural language command
- The smart home state is loaded from smart_home.json
- GPT generates a structured JSON rule
- The rule is validated against the smart home environment
- The system reports whether the rule is valid or mismatched

## Example Input
```t
  Turn on the bedroom AC when temperature is above 27
```

## Example Generated Rule
```t

{
  "trigger": {
    "type": "sensor",
    "source": "bedroom.temperature_sensor",
    "operator": "greater_than",
    "value": "27"
  },
  "action": {
    "device": "bedroom.ac",
    "command": "turn_on"
  }
}
```

## Hallucination Checks Implemented So Far

The current prototype can detect:

- invalid room references
- invalid device references
- unsupported actions
- invalid sensor references
- some user intent mismatches


## Installation
1. Clone the repository
2. Install dependencies:
  pip install -r requirements.txt

3. Create a .env file and add your OpenAI API key:
   OPENAI_API_KEY=your_api_key_here

## Run the project
  python app.py


## Notes
- The .env file is not included for security reasons
- Use .env.example as a template
- This is an active student project and the system is still under development


## Future Work

Planned next steps include:
- mitigation of hallucinated rules
- conflict detection between rules
- execution simulation
- synthetic dataset generation
- evaluation of baseline vs validated system