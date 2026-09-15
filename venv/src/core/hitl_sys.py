import sys

HITL_TOOLS = {
    "delete_file",
    "delete_directory",
    "create_directory",
    "write_file"
}

def trigger_HITL(tool_name: str, agent_name: str, task_description: str = "") -> bool:
    try:

        if not isinstance(tool_name, str):
            tool_name = getattr(tool_name, "name", str(tool_name))

        if tool_name in HITL_TOOLS:
            print(f"\n\033[33m[HITL SAFETY CHECKPOINT TRIGGERED]\033[0m")
            print(f"  ├─ Intercepted Tool: \033[1;31m{tool_name}\033[0m")
            print(f"  ├─ Target Sub_agent: \033[1m{agent_name}\033[0m")
            print(f"  └─ Action Payload: {task_description}...")
            
            while True:
                try:
                    print(f"Execution of")
                    user_input = input("\n\033[1;36mDo you approve this execution? (y/n): \033[0m").strip().lower()
                    if user_input in ['y', 'yes']:
                        print("\033[32m[APPROVED] Proceeding with task execution...\033[0m")
                        return True
                    elif user_input in ['n', 'no']:
                        print("\033[31m[REJECTED] Action canceled by human supervisor.\033[0m")
                        return False
                    else:
                        print("Invalid input. Please enter 'y' or 'n'.")
                except KeyboardInterrupt:
                    print("\nExecution interrupted by user.")
                    sys.exit(0)
        else:
            return True
    except Exception as e:
        return False