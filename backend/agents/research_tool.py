

from backend.utils.llm import llm_stream

def research_tool(query):
    print(f"Researching topic: {query}")
    return llm_stream(f"""
Research the topic: {query}

Include:
- facts
- statistics
- real sources
- cite sources like [1], [2]

At the end, list sources.
""")