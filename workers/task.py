
from workers.celery_app import celery
import redis
import json

from backend.utils.llm import llm_stream

r = redis.Redis(host="localhost", port=6379, db=0)


@celery.task
def execute_convoy(task_id, convoy):
    channel = f"stream:{task_id}"

    print("Convoy received:", convoy)

    data_store = {}

    try:
        for bead in convoy:
            step = bead["type"]

            r.publish(channel, f"\n\n⚙️ {step.upper()}...\n")

            if step == "research":
                query = bead["input"]

                r.publish(channel, f"Running multiple research:\n\n")
                

                prompts = [
                    f"Research from news sources: {query}",
                    f"Research from academic perspective: {query}",
                    f"General overview: {query}"
                    ]


                allresults = []

                for p in prompts:
                    full_text = ""

                    for chunk in llm_stream(p):
                        try:
                            data = json.loads(chunk)
                            text = data.get("response", "")

                            if text:
                                r.publish(channel, text)
                                full_text += text

                        except Exception as e:
                            print("Parse error:", e)
                            continue

                    allresults.append(full_text)

                combined_results = "\n\n".join(allresults)
                data_store["research"] = combined_results    
            
                

        
            # SUMMARIZER AGENT
     
            elif step == "summarize":
                full_text = ""

                for chunk in llm_stream(f"Summarize this:\n{data_store.get('research', '')}"):
                    try:
                        data = json.loads(chunk)
                        text = data.get("response", "")

                        if text:
                            r.publish(channel, text)
                            full_text += text

                    except Exception as e:
                        print("Parse error:", e)
                        continue

                data_store["summary"] = full_text

            # CRITIC AGENT
      
            elif step == "critic":
                full_text = ""

                for chunk in llm_stream(f"Critically improve this:\n{data_store.get('summary', '')}"):
                    try:
                        data = json.loads(chunk)
                        text = data.get("response", "")

                        if text:
                            r.publish(channel, text)
                            full_text += text

                    except Exception as e:
                        print("Parse error:", e)
                        continue

                data_store["critic"] = full_text

            #  WRITER AGENT
       
            elif step == "write":
                input_text = data_store.get("critic") or data_store.get("summary") or data_store.get("research", "")

                full_text = ""

                for chunk in llm_stream(f"""
Write a professional report based on this:

{input_text}

Structure:
- Introduction
- Key Points
- Analysis
- Conclusion

Include:
- citations in [1] format
- sources at end

"""):
                    try:
                        data = json.loads(chunk)
                        text = data.get("response", "")

                        if text:
                            r.publish(channel, text)
                            full_text += text

                    except Exception as e:
                        print("Parse error:", e)
                        continue

                data_store["final"] = full_text

    
        #DONE
    
        r.publish(channel, "\n\n COMPLETED\n")
        r.publish(channel, "[DONE]")

        return data_store.get("final", "")

    except Exception as e:
        print("Task error:", e)

        r.publish(channel, "\n\n ERROR OCCURRED\n")
        r.publish(channel, "[DONE]")

        return str(e)