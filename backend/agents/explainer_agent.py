
from backend.utils.llm import llm_stream

def explainer_agent(query: str):
    prompt = f"""
Explain clearly and simply:

{query}

Make it beginner-friendly.
"""

    for text in llm_stream(prompt):
        yield text