
from backend.utils.llm import llm_stream

def compare_agent(query: str):
    prompt = f"""
Compare the following:

{query}

Include:
- Differences
- Pros/Cons
- Use cases
"""

    for text in llm_stream(prompt):
        yield text