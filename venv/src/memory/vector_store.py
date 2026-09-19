import os
from typing import List
from langchain_community.vectorstores import Chroma 
from langchain_core.documents import Document

# Persistent storage directory for local VectorDB
PERSIST_DIRECTORY = os.path.join(os.path.dirname(__file__), "../../chroma_db") 

class AgentMemoryStore:
    """Persistent Long-Term Semantic Memory Engine using ChromaDB."""

    def __init__(self, collection_name: str = "agent_execution_memory"):
        # For lightweight local setups, use a local embedding strategy or OpenAI embeddings if configured
        # Fallback to local Chroma default embeddings or LangChain wrapper
        self.vector_db = Chroma(
            collection_name=collection_name,
            persist_directory=PERSIST_DIRECTORY
        )

    def save_task_memory(self, time_stamp: str, main_task: str, task_id: int, task_desc: str, worker: str, result: str):
        """Persist a completed task observation as a searchable document vector."""
        content = f"Task ID: {task_id}\nWorker: {worker}\nDescription: {task_desc}\nResult:\n{result}"
        metadata = {
            "date_of_event": time_stamp,
            "main_task": main_task,
            "task_id": str(task_id),
            "worker": worker,
            "type": "task_observation"
        }
        doc = Document(page_content=content, metadata=metadata)
        self.vector_db.add_documents([doc])

    def save_general_memory(self, time_stamp: str, memory: str, agent: str, description: str):
        """Save general queries and summaries of every session"""
        content = f"Session summary on {time_stamp}"
        metadata = {
            "Time_of_save": time_stamp,
            "agent": agent,
            "description": description,
            "saved_memory": memory,
            "type": "general_memory"
        }
        doc = Document(page_content=content, metadata=metadata)
        self.vector_db.add_documents([doc])

    def query_relevant_memories(self, query: str, top_k: int = 3) -> List[str]:
        """Retrieve top_k semantically relevant past task results given a query string."""
        results = self.vector_db.similarity_search(query, k=top_k)
        return [doc.page_content for doc in results]

# Global singleton instance
memory_store = AgentMemoryStore()