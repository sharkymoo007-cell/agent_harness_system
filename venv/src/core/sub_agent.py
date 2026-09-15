from langchain.agents import create_agent
from src.core.llm import llm_flash, llm_pro
from src.tools.basic_tools import calculate, write_file, read_file, list_dir, system_clock
from src.tools.memory_tools import search_long_term_memory
from src.tools.search_tools import web_search
from langgraph.checkpoint.memory import MemorySaver

public_tools = [read_file, list_dir, system_clock]
memory = MemorySaver()

# 1. Search Specialist Agent
search_agent = create_agent(
    llm_flash,
    [web_search, search_long_term_memory] + public_tools,
    system_prompt="""
    You are a dedicated 'Information Search Specialist'.
    Your role is to perform accurate and up-to-date information retrieval based on given instructions.
    Keep your output objective, concise, and focused solely on providing the requested core facts without your own opinion.
    """,
    checkpointer=memory,
    interrupt_before=["tools"]
)

# 2. Computation & Logic Analyst Agent (Equipped with Calculator & System Clock)
coder_agent = create_agent(
    llm_pro,
    [calculate] + public_tools,
    system_prompt="""
    You are a dedicated 'Data Computation and Logic Analysis Specialist'.
    Your role is to execute complex numerical operations, data structured processing, code writing and logical reasoning.
    For ANY mathematical operations, you MUST invoke the 'calculate' tool. Maintain high precision and rigor.
    """,
    checkpointer=memory,
    interrupt_before=["tools"]

)

# 3. File & System Management Worker (Equipped with File I/O tools)
file_agent = create_agent(
    llm_flash,
    [write_file] + public_tools,
    system_prompt="""You are a dedicated 'System and File Management Specialist'.
    Your role is to manage file operations including reading content, writing persistent logs/reports, or inspecting directories.
    Ensure file outputs are formatted clearly and structured professionally.

    IMPORTANT: new files MUST be created under the './agent_creations' directory
    """,
    checkpointer=memory,
    interrupt_before=["tools"]
)

WORKER_MAP = {
    "search_agent": search_agent,
    "coder_agent": coder_agent,
    "file_agent": file_agent
}