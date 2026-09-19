from langchain_core.tools import tool
from src.memory.vector_store import memory_store
from datetime import datetime

@tool
def search_long_term_memory(query: str) -> str:
    """
    Search long-term memory for past execution results, saved files, or previous user tasks.
    Use this when you need information about what was generated or executed in past sessions.
    """
    memories = memory_store.query_relevant_memories(query, top_k=5)
    if not memories:
        return "No relevant past memories found."
    
    return "\n---\n".join(memories).join("\n---\n")

@tool
def save_memory(content: str) -> str:
    """Save important imformation or content worth memorizing into the database"""
    try:
        memory_store.save_general_memory(time_stamp=f"{datetime.now().strftime("%d/%m/%Y, %H")}",
                                        agent="memory_agent",
                                        description="memory actively saved by main agent during session",
                                        memory=content)
        if content:
            return "Memory successfully saved."
        else:
            return "No content input, please retry."
    except Exception as e:
        return f"[ERROR]: save memory FAILED due to error {e}"
    