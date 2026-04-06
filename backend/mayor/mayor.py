import json
from backend.utils.llm import call_llm


def detect_intents(query: str):
    prompt = f"""
You are an NLP system.

Analyze the user query and extract ALL intents.

Possible intents:
- backend
- code
- explain
- research
- summarize
- compare
- creative

Return JSON like:
[
  {{ "intent": "backend", "reason": "user asked to build API" }},
  {{ "intent": "explain", "reason": "user asked for explanation" }}
]

Query:
{query}
"""

    try:
        response = call_llm(prompt)

        start = response.find("[")
        end = response.rfind("]") + 1
        json_str = response[start:end]

        return json.loads(json_str)

    except Exception as e:
        print("Intent detection error:", e)
        return []
    

def split_tasks(query: str):
    prompt = f"""
Break the query into atomic tasks.

Each task should be a clear step.

Return JSON like:
[
  {{ "task": "create CRUD API using FastAPI" }},
  {{ "task": "explain the code" }}
]

Query:
{query}
"""

    try:
        response = call_llm(prompt)

        start = response.find("[")
        end = response.rfind("]") + 1
        json_str = response[start:end]

        return json.loads(json_str)

    except Exception as e:
        print("Task split error:", e)
        return [{"task": query}]
    


def create_convoy(query: str):
    print(" Query:", query)

    intents = detect_intents(query)
    tasks = split_tasks(query)

    print(" Intents:", intents)
    print(" Tasks:", tasks)

    convoy = []

    intent_to_agent = {
        "backend": "backend",
        "code": "code",
        "explain": "explain",
        "research": "research",
        "summarize": "summarize",
        "compare": "compare",
        "creative": "creative"
    }

    for i, task in enumerate(tasks):
        task_text = task["task"]

        matched_intent = None

        for intent_obj in intents:
            intent = intent_obj.get("intent")

            if intent in task_text.lower():
                matched_intent = intent
                break

        if not matched_intent and intents:
            matched_intent = intents[0]["intent"]

        agent_type = intent_to_agent.get(matched_intent, "research")

        step = {"type": agent_type}

        if i == 0:
            step["input"] = task_text

        convoy.append(step)

    if convoy[-1]["type"] not in ["write", "explain"]:
        convoy.append({"type": "write"})

    print(" Final Convoy:", convoy)

    return convoy