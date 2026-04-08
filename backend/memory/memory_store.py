import chromadb

from chromadb.utils import embedding_functions

chroma_client = chromadb.Client(
    chromadb.config.Settings(
        persist_directory="./chroma_db"
    )
)
collection = chroma_client.get_or_create_collection(
    name="agent_memory"
)

def store_memory(task_id, step, content):
    collection.add(
        documents=[content],
        metadatas=[{"task_id": task_id, "step": step}],
        ids=[f"{task_id}-{step}-{hash(content)}"]
    )



def get_memory(query, task_id):
    results = collection.query(
        query_texts=[query],
        n_results=3
    )

    docs = results.get("documents", [[]])[0]
    return "\n".join(docs)