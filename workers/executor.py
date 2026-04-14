from celery import chain

from workers.polecats import run_step

def execute_convoy(task_id, convoy):
    tasks = []

    for bead in convoy:
        tasks.append(
            run_step.s(task_id, bead["type"], bead.get("input", ""))
        )

    job = chain(*tasks)
    job.apply_async()

    return task_id