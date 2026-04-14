import json
from backend.utils.llm import call_llm




def create_plan(query: str):
    prompt = f"""
You are an AI task planner.

Break the user query into ordered steps.
For EACH step assign the correct agent.

Available agents:
- explain → for explaining any topics
- research → for gathering knowledge and deep research
- backend_fastapi → for building backend fast APIs
- backend_nodeapi → for building backend node APIs
- generate_code → for writing code
- summarize → for summarizing the content
- compare → for comparisons between tow or more things
- creative → for writing content
- write → for final structured output


CRITICAL INSTRUCTIONS (MUST FOLLOW STRICTLY):

1. If query contains the word "explain":
   - Return ONLY ONE step
   - Agent must be "explain"
   - DO NOT include research or write

2. If query contains "research":
   - Return ONLY ONE step
   - Agent must be "research"

3. If query contains "backend fastapi":
   - Return ONLY ONE step
   - Agent must be "backend_fastapi"

4. If query contains "backend nodeapi":
   - Return ONLY ONE step
   - Agent must be "backend_nodeapi"

5. If query contains "generate code" or "write code":
   - Return ONLY ONE step
   - Agent must be "generate_code"

6. If query contains "summarize":
   - Return ONLY ONE step
   - Agent must be "summarize"

7. If query contains "compare":
   - Return ONLY ONE step
   - Agent must be "compare"

8. ONLY if none of the above match:
   - You may create multi-step plan


STRICT RULE:
- DO NOT add extra steps
- DO NOT use research unless explicitly asked

Return STRICT JSON like this:

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



from celery import chain

from workers.polecats import run_step

def execute_convoy(task_id, convoy):
    tasks = []

    for bead in convoy:
        tasks.append(
            run_step(task_id, bead["type"], bead.get("input", ""))
        )

    job = chain(*tasks)
    job.apply_async()

    return task_id

