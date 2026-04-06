import json
from backend.utils.llm import call_llm


def validate_convoy(convoy, query):
    valid_types = {
        "research", "summarize", "critic", "write",
        "backend", "code", "explain", "compare", "plan", "creative"
    }

    fixed = []

    for step in convoy:
        if not isinstance(step, dict):
            continue

        step_type = step.get("type")

        if step_type not in valid_types:
            continue

        # ensure research has input
        if step_type == "research" and "input" not in step:
            step["input"] = query

        fixed.append(step)

    if not fixed:
        fixed = [{"type": "research", "input": query}]

    if fixed[-1]["type"] not in ["write", "code", "backend"]:
        fixed.append({"type": "write"})

    return fixed

def create_convoy(query: str):
    print("Creating convoy for query:", query)

    planning_prompt = f"""
You are an AI task planner.

Break the user query into steps using these agents:

Available agents:
- research → gather information
- summarize → shorten content
- critic → improve / analyze
- write → final output
- backend → create APIs (FastAPI)
- code → write/debug code
- explain → explain concepts
- compare → compare topics
- plan → create step-by-step plan
- creative → generate stories/content

Rules:
- Always add input only for first step
- Use only relevant agents according to query
- Keep steps minimal

Return ONLY JSON list like:
[
  {{ "type": "research", "input": "..." }},
  {{ "type": "summarize" }},
  {{ "type": "write" }}
]

Query:
{query}
"""

    response = call_llm(planning_prompt)

    print("Raw LLM response:", response)

    start = response.find("[")
    end = response.rfind("]") + 1
    json_str = response[start:end]

    convoy = json.loads(json_str)

    convoy = validate_convoy(convoy, query)

    print("Final convoy:", convoy)

    return convoy


