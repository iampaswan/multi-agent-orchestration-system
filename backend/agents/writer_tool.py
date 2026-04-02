
from backend.utils.llm import llm_stream

def writer_tool(data):
    print(f"Writing report based on data: {data}")
    return llm_stream(
        f"""
Write a professional, well-structured research report based on this:

{data}

Structure:
- Introduction
- Key Insights
- Challenges
- Future Outlook
- Conclusion
"""
    )









