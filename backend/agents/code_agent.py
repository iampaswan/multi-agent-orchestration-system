
from backend.utils.llm import llm_stream

def code_agent(query: str):
    prompt = f"""
You are an expert programmer.

Task:
{query}


Return:
- Clean code
- Fix bugs if any
- No explanation unless needed
"""

    for text in llm_stream(prompt):
        yield text