import os
import shutil
from datetime import datetime
from src.core.main_agent import create_initial_plan, review_and_replan
from src.core.sub_agent import WORKER_MAP
from src.logger import AgentLogger
from src.memory.vector_store import memory_store
from src.memory.context_governor import context_governor
from src.core.hitl_sys import trigger_HITL

def run_multi_agent_pipeline(user_input: str, config: dict) -> str:

    # 1. main agent generate initial roadmap
    AgentLogger.log_header("MAIN: CREATING EXECUTION PLAN")
    plan = create_initial_plan(user_input)   # initialize Plan

    print(f"\033[35m[MANAGER PLAN INITIALIZED]\033[0m Goal: {plan.original_goal}")
    for st in plan.subtasks:
        print(f"├─ Task {st.task_id} [{st.assigned_Agent}]: {st.task_description}")

    step_count = 0
    max_step = 10

    while not plan.is_completed and step_count < max_step:
        step_count += 1
        current_subtask = plan.subtasks[plan.current_task_index]
        agent_name = current_subtask.assigned_Agent

        AgentLogger.log_header(f"STEP {step_count}: DISPATCHING TO [{agent_name.upper()}]")
        print(f"\033[33m[TASK EXECUTION]\033[0m: {current_subtask.task_description}")

        # 2. Dispatch subtask to corresponding worker agent
        worker_agent = WORKER_MAP.get(agent_name)
        if not worker_agent:
            last_output = f"Execution Error: Worker '{agent_name}' is not registered in WORKER_MAP."
        else:
            # Execute sub_agent loop
            response = worker_agent.invoke(
                {"messages": [("user", current_subtask.task_description+"\nThe ORIGINAL OUTPUT of previous agents in this project are stored in the './temporary_db' directory, you may browse if needed.\n")]},
                config=config
            )

            current_status = worker_agent.get_state(config)

            while current_status.next and "tools" in current_status.next:
                last_msg = current_status.values["messages"][-1]

                for call in last_msg.tool_calls:
                    tool_name = call["name"]
                    tool_args = call["args"]
                    id = call["id"]
                    
                    approved = trigger_HITL(
                        tool_name=tool_name,
                        agent_name=current_subtask.assigned_Agent,
                        task_description=tool_args
                    )
                    
                    if not approved:
                        denial_message = {
                            "role": "tool",
                            "tool_call_id": id,
                            "name": tool_name,
                            "content": "User Rejected Operation: Permission denied by human supervisor."
                        }
                        worker_agent.update_state(
                            config,
                            {"messages": [denial_message]},
                            as_node="tools"
                        )
                        print("\033[31m[REJECTED] Blocking Tool execution and notifying agent...\033[0m")
                        break                    

                response = worker_agent.invoke(None,config=config)
                current_status = worker_agent.get_state(config)

            last_output = response["messages"][-1].content
            with open(f"./temporary_db/Task_{plan.current_task_index}_Output.txt", "w", encoding="utf-8") as f:
                f.write(last_output)

            # Governance: Persist raw result to Long-Term Semantic VectorDB
            memory_store.save_task_memory(
                time_stamp=f"Date of event:{datetime.now().strftime("%d/%m/%Y")}",
                main_task=plan.original_goal,
                task_id=current_subtask.task_id,
                task_desc=current_subtask.task_description,
                worker=current_subtask.assigned_Agent,
                result=last_output
            )
            
            # Compress observation for Manager's Short-Term Context
            compressed_result = context_governor.compress_observation(last_output, max_length=600)

            AgentLogger.log_thought(f"Sub_agent Observation:\n{compressed_result}")

        # 3. Manager reviews worker output and dynamically replans trajectory
        AgentLogger.log_header(f"MAIN: REVIEWING TASK {current_subtask.task_id} RESULT")
        plan = review_and_replan(plan, compressed_result)
        
        if plan.is_completed:
            break

    if plan.final_summary:
        shutil.rmtree('./temporary_db', ignore_errors=True) 
        os.makedirs('./temporary_db', exist_ok=True)
        return plan.final_summary
    else:
        return "Task execution reached safety threshold without completion."