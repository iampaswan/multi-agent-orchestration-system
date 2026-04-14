from workers.celery_app import celery
import redis
import json
import os

from backend.agents import (
    research_agent,
    summarizer_agent,
    writer_agent,
    backend_fastapi_agent,
    generate_code_agent,
    explainer_agent,
)

r = redis.Redis(host="localhost", port=6379, db=0)


def get_rig_path(task_id):
    path = f"./workspace/rigs/{task_id}"
    os.makedirs(path, exist_ok=True)
    return path


def store(task_id, key, value):
    r.set(f"{task_id}:{key}", value)


def load(task_id, key):
    val = r.get(f"{task_id}:{key}")
    return val.decode() if val else ""


@celery.task(bind=True)
def run_step(self, task_id, step_type, input_text):
    channel = f"stream:{task_id}"

    r.publish(channel, json.dumps({
        "type": "step",
        "step": step_type
    }))

    rig_path = get_rig_path(task_id)

    full_text = ""

    try:
        # 🔹 Example: research
        if step_type == "research":
            for chunk in research_agent(input_text):
                data = json.loads(chunk)
                text = data.get("response", "")

                if text:
                    r.publish(channel, text)
                    full_text += text

            store(task_id, "research", full_text)

        # 🔹 summarize
        elif step_type == "summarize":
            context = load(task_id, "research")

            for chunk in summarizer_agent(f"Summarize:\n{context}"):
                data = json.loads(chunk)
                text = data.get("response", "")

                if text:
                    r.publish(channel, text)
                    full_text += text

            store(task_id, "summary", full_text)

        # 🔹 write
        elif step_type == "write":
            context = (
                load(task_id, "summary")
                or load(task_id, "research")
            )

            for chunk in writer_agent(context):
                data = json.loads(chunk)
                text = data.get("response", "")

                if text:
                    r.publish(channel, text)
                    full_text += text

            store(task_id, "final", full_text)

            # 💾 write to file (RIG)
            with open(f"{rig_path}/output.md", "w") as f:
                f.write(full_text)

        # 🔹 backend_fastapi
        elif step_type == "backend_fastapi":
            for chunk in backend_fastapi_agent(input_text):
                data = json.loads(chunk)
                text = data.get("response", "")

                if text:
                    r.publish(channel, text)
                    full_text += text

            store(task_id, "backend", full_text)

            with open(f"{rig_path}/app.py", "w") as f:
                f.write(full_text)

        # 🔹 generate_code
        elif step_type == "generate_code":
            for chunk in generate_code_agent(input_text):
                data = json.loads(chunk)
                text = data.get("response", "")

                if text:
                    r.publish(channel, text)
                    full_text += text

            store(task_id, "code", full_text)

        # 🔹 explain
        elif step_type == "explain":
            for chunk in explainer_agent(input_text):
                data = json.loads(chunk)
                text = data.get("response", "")

                if text:
                    r.publish(channel, text)
                    full_text += text

            store(task_id, "explain", full_text)

        r.publish(channel, json.dumps({
            "type": "done",
            "step": step_type
        }))

        return task_id

    except Exception as e:
        r.publish(channel, f"ERROR: {str(e)}")
        raise e