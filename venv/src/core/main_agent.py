import re
from langchain_core.messages import SystemMessage, HumanMessage
from src.core.llm import llm_flash
from langchain_core.output_parsers import PydanticOutputParser
from src.core.schemas import ExecutionPlan
from src.prompts import PLANNER_SYSTEM_PROMPT, REPLANNER_SYSTEM_PROMPT

parser = PydanticOutputParser(pydantic_object=ExecutionPlan)
def _extract_json_string(text: str) -> str:
    """Hard-parsing fallback: Extract raw JSON content by stripping markdown tags and surrounding prose."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return match.group(0)
    return text

def invoke_llm_with_hard_defense(messages: list, max_retries: int = 3) -> ExecutionPlan:
    """Hard-defense execution pipeline combining regex extraction, strict Pydantic validation, and self-correction retry."""
    current_messages = list(messages)
    
    for attempt in range(max_retries):
        response = llm_flash.invoke(current_messages)
        raw_text = response.content
    
        try:
            # Layer 1 & 2: Regex extraction followed by strict Pydantic parsing
            clean_json_str = _extract_json_string(raw_text)
            plan = parser.parse(clean_json_str)
            return plan  # Return validated object on success
            
        except Exception as e:
            # Layer 3: Self-correction retry loop
            error_msg = f"Your last output failed JSON validation. #Error: {str(e)}. Please correct your response and strictly follow the JSON Schema."
            print(f"\033[33m[HARD DEFENSE TRIGGERED]\033[0m Validation failed (Attempt {attempt + 1}/{max_retries}). Feeding error trace back to LLM...")
            
            # Append failed response and error feedback to prompt context for self-correction
            current_messages.append(HumanMessage(content=raw_text))
            current_messages.append(HumanMessage(content=error_msg))
            
    raise RuntimeError(f"Manager failed to generate a valid ExecutionPlan object after {max_retries} attempts.")

def create_initial_plan(user_goal: str) -> ExecutionPlan:
    """Generate an initial structured execution plan from user intent."""
    messages = [
        SystemMessage(content=PLANNER_SYSTEM_PROMPT),
        HumanMessage(content=f"User Goal: {user_goal}")
    ]
    plan: ExecutionPlan = invoke_llm_with_hard_defense(messages)
    return plan

def review_and_replan(plan: ExecutionPlan, last_subAgent_output: str) -> ExecutionPlan:
    """Evaluate step performance and update the master execution roadmap dynamically."""
    current_task = plan.subtasks[plan.current_task_index]
    
    prompt = f"""
    Master Goal: {plan.original_goal}
    Current Progress: Step {plan.current_task_index + 1} of {len(plan.subtasks)}
    Active Subtask Description: {current_task.task_description}
    Assigned Worker: {current_task.assigned_Agent}
    Observation Output from Worker:
    ---
    {last_subAgent_output}
    ---
    Here is the plan structure again:
    {plan}

    Review the observation and update the ExecutionPlan status. If all steps are complete, formulate the 'final_summary'.
    
    IMPORTANT: you MUST NOT change the "assigned_Agent" UNLESS the plan trajectory needs to be changed, ONLY modify the part of the "plan" that you are specified to.
    """
    messages = [
        SystemMessage(content=REPLANNER_SYSTEM_PROMPT),
        HumanMessage(content=prompt)
    ]
    updated_plan: ExecutionPlan = invoke_llm_with_hard_defense(messages)
    return updated_plan