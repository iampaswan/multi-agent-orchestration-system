import json
from backend.utils.llm import call_llm







def create_plan(query: str):
    prompt = f"""
You are an AI task planner.

Break the user query into ordered steps.
For EACH step assign the correct agent.

Available agents:
- research → for gathering knowledge
- backend → for building APIs
- generate_code → for writing code
- explain → for explaining things
- summarize → for summarizing
- compare → for comparisons
- creative → for writing content
- write → for final structured output

Return STRICT JSON:

[
  {{
    "step": 1,
    "agent": "research",
    "input": "research FastAPI"
  }},
  {{
    "step": 2,
    "agent": "backend",
    "input": "build todo API using FastAPI"
  }},
  {{
    "step": 3,
    "agent": "explain",
    "input": "explain the backend code"
  }},
  {{
    "step": 4,
    "agent": "write",
    "input": "combine everything into final answer"
  }}
]

Query:
{query}


Rules:
- Use research BEFORE coding if topic is unknown
- Use backend for API building
- Use generate_code for code writing
- Use explain AFTER code generation
- Always end with write
- Keep steps minimal but complete


"""
    response = call_llm(prompt)

    start = response.find("[")
    end = response.rfind("]") + 1
    return json.loads(response[start:end])



def create_convoy(query: str):
    print("Query:", query)

    plan = create_plan(query)

    convoy = []
    print("Creating Convoy..")

    for step in plan:
        convoy.append({
            "type": step["agent"],
            "input": step.get("input", "")
        })

    print("Final Convoy:", convoy)
    return convoy