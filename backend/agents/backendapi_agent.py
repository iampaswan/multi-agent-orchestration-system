
from backend.utils.llm import llm_stream

def backend_agent(query: str):
    prompt = f"""
You are a senior backend engineer.

Create a FastAPI backend for:
{query}

Rules:
- Return COMPLETE working code
- No missing values
- No placeholders like status_code=
- Use FastAPI best practices
- Include imports
- Ensure code is executable
- Wrap response in triple backticks

Wrap output STRICTLY like:

```python
# code here

"""

    for text in llm_stream(prompt):
        yield text