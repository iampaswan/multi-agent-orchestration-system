
from workers.celery_app import celery
import redis
import json

from backend.agents.research_agent import research_agent
from backend.agents.summarizer_agent import summarizer_agent
from backend.agents.critic_agent import critic_agent
from backend.agents.writer_agent import writer_agent  

from backend.agents.backendapi_agent import backend_agent
from backend.agents.code_agent import code_agent
from backend.agents.explainer_agent import explainer_agent
from backend.agents.compare_agent import compare_agent
from backend.agents.creative_agent import creative_agent


r = redis.Redis(host="localhost", port=6379, db=0)


@celery.task
def execute_convoy(task_id, convoy):
    channel = f"stream:{task_id}"

    print("Convoy received:", convoy)

    data_store = {}

    try:
        for bead in convoy:
            step = bead["type"]

            r.publish(channel, f"\n\n----- Running -> {step.upper()} -----\n")

            if step == "research":
                query = bead["input"]

                r.publish(channel, f"Running multiple research:\n\n")
                r.publish(channel, json.dumps({
                        "type": "step",
                        "step": step
                }))
                

                prompts = [
                    f"Technical analysis of: {query}",
                    # f"Economic and industry impact of: {query}",
                    # f"Latest news and developments: {query}",
                    # f"Academic research insights on: {query}"
                    ]


                allresults = []

                for p in prompts:
                    r.publish(channel, f"\n\nRuinning >> {p}\n")
                  
                    full_text = ""

                    for chunk in research_agent(p):
                        try:
                            data = json.loads(chunk)
                            text = data.get("response", "")

                            if text:
                                r.publish(channel, text)
                                r.publish(channel, json.dumps({
                                     "type": "log",
                                     "step": step,
                                     "content":text[:100],
                          }))
                                full_text += text

                        except Exception as e:
                            print("Parse error:", e)
                            continue

                    allresults.append(full_text)

                combined_results = "\n\n".join(allresults)
                data_store["research"] = combined_results    

            elif step == "summarize":
                r.publish(channel, json.dumps({
                        "type": "step",
                        "step": step
                    }))
                full_text = ""

                for chunk in summarizer_agent(f"Summarize this:\n{data_store.get('research', '')}"):
                    try:
                        data = json.loads(chunk)
                        text = data.get("response", "")

                        if text:
                            r.publish(channel, text)
                            r.publish(channel, json.dumps({
                                     "type": "log",
                                     "step": step,
                                     "content":text[:100],
                          }))
                            full_text += text

                    except Exception as e:
                        print("Parse error:", e)
                        continue

                data_store["summary"] = full_text

            elif step == "critic":
                r.publish(channel, json.dumps({
                        "type": "step",
                        "step": step
                    }))
                full_text = ""

                for chunk in critic_agent(f"Critically improve this:\n{data_store.get('summary', '')}"):
                    try:
                        data = json.loads(chunk)
                        text = data.get("response", "")

                        if text:
                            r.publish(channel, text)
                            r.publish(channel, json.dumps({
                                     "type": "log",
                                     "step": step,
                                      "content":text[:100],
                          }))
                            full_text += text

                    except Exception as e:
                        print("Parse error:", e)
                        continue

                data_store["critic"] = full_text

            elif step == "write":
                r.publish(channel, json.dumps({
                        "type": "step",
                        "step": step
                    }))
                input_text = data_store.get("critic") or data_store.get("summary") or data_store.get("research", "")

                full_text = ""
                



                for chunk in writer_agent(f"""
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
                            r.publish(channel, json.dumps({
                                     "type": "log",
                                     "step": step,
                                      "content":text[:100],
                          }))
                            full_text += text

                    except Exception as e:
                        print("Parse error:", e)
                        continue

                data_store["final"] = full_text
            
            elif step == "backend":
                input_text = bead.get("input", "")
                full_text = ""

                r.publish(channel, json.dumps({
                        "type": "step",
                        "step": step
                    }))

                for chunk in backend_agent(input_text):
                    try:
                        data = json.loads(chunk)
                        text = data.get("response", "")

                        if text:
                            r.publish(channel, text)
                            r.publish(channel, json.dumps({
                                     "type": "log",
                                     "step": step,
                                     "content":text[:100],
                          }))
                            full_text += text

                    except Exception as e:
                        print("Parse error:", e)
                        continue

                data_store["backend"] = full_text
            
            elif step == "code":
                r.publish(channel, json.dumps({
                        "type": "step",
                        "step": step
                    }))
                input_text = bead.get("input", "")
                full_text = ""

                for chunk in code_agent(input_text):
                    try:
                        data = json.loads(chunk)
                        text = data.get("response", "")

                        if text:
                            r.publish(channel, text)
                            r.publish(channel, json.dumps({
                                     "type": "log",
                                     "step": step,
                                     "content":text[:100],
                          }))
                            full_text += text

                    except Exception as e:
                        print("Parse error:", e)
                        continue

                data_store["code"] = full_text
     
            elif step == "explain":
                r.publish(channel, json.dumps({
                        "type": "step",
                        "step": step
                    }))
                input_text = bead.get("input", "")

                full_text = ""

                for chunk in explainer_agent(input_text):
                    try:
                        data = json.loads(chunk)
                        text = data.get("response", "")

                        if text:
                            r.publish(channel, text)
                            r.publish(channel, json.dumps({
                                     "type": "log",
                                     "step": step,
                                      "content":text[100],
                          }))
                            full_text += text

                    except Exception as e:
                        print("Parse error:", e)
                        continue

                data_store["explain"] = full_text           
     
            elif step == "compare":
                r.publish(channel, json.dumps({
                        "type": "step",
                        "step": step
                    }))
                input_text = bead.get("input", "")

                full_text = ""

                for chunk in compare_agent(input_text):
                    try:
                        data = json.loads(chunk)
                        text = data.get("response", "")

                        if text:
                            r.publish(channel, text)
                            r.publish(channel, json.dumps({
                                     "type": "log",
                                     "step": step,
                                      "content":text[100],
                          }))
                            full_text += text

                    except Exception as e:
                        print("Parse error:", e)
                        continue

                data_store["compare"] = full_text     
        
            elif step == "creative":
                r.publish(channel, json.dumps({
                        "type": "step",
                        "step": step
                    }))
                input_text = bead.get("input", "")

                full_text = ""

                for chunk in creative_agent(input_text):
                    try:
                        data = json.loads(chunk)
                        text = data.get("response", "")

                        if text:
                            r.publish(channel, text)
                            r.publish(channel, json.dumps({
                                     "type": "log",
                                     "step": step,
                                      "content":text[100],
                          }))
                            full_text += text

                    except Exception as e:
                        print("Parse error:", e)
                        continue

                data_store["creative"] = full_text        
        
        
        
        #DONE

        r.publish(channel, json.dumps({
             "type": "done",
             "step": step
             }))
    
        r.publish(channel, "\n\n COMPLETED\n")

        r.publish(channel, "[DONE]")

        return data_store.get("final", "")

    except Exception as e:
        print("Task error:", e)

        r.publish(channel, "\n\n ERROR OCCURRED\n")
        r.publish(channel, "[DONE]")

        return str(e)