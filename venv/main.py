from src.logger import AgentLogger
from src.core.engine import run_multi_agent_pipeline
from src.memory.context_governor import context_governor
from src.memory.vector_store import memory_store
from datetime import datetime

def main():
    print("=" * 60)
    print("Initializing agent......(based on DeepSeek and LangGraph)")
    print("Hint: Type in 'exit' or 'quit' to leave")
    print("=" * 60)
    
    config = {"configurable": {"thread_id": "session_001"}}
    user_input = ""
    
    while True:
        try:
            new_input = input("\nUser: ").strip()
            user_input += new_input
            if not new_input:
                continue
            if new_input.lower() in ["exit", "quit", "q", "e"]:
                if input("\033[31m[SAVE MEMORY?](Y/N): \033[0m")=="Y":
                    memory_store.save_general_memory(time_stamp=f"{datetime.now().strftime("%d/%m/%Y, %H")}:00", 
                                                    description="The summary of the all history conversations in the session",
                                                    agent="Main agent",
                                                    memory=context_governor.conversation_summary(user_input))
                print("Goodbye! Exiting system...")
                break
            
            AgentLogger.log_header("AGENT INFERENCE START")
            final_resp = run_multi_agent_pipeline(user_input, config)
            AgentLogger.log_header("AGENT INFERENCE END")
            
            if final_resp:
                user_input += f"\n---\nYour previous response\n---\n{final_resp}\n---\n"
                print(f"\n\033[1;35m[FINAL OUTPUT]:\033[0m\n{final_resp}")
                
        except Exception as e:
            print(f"\nERROR[runtime error]: {str(e)}")

if __name__ == "__main__":
    main()