
from backend.utils.llm import llm_stream

def creative_agent(query: str):
    prompt = f"""
Create engaging content:

{query}

Be creative and interesting.
"""

    for text in llm_stream(prompt):
        yield text