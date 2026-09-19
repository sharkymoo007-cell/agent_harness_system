from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class SubTask(BaseModel):
    """The definiton of the individual task given by the main agent"""

    task_id: int = Field(description="the id of each subtask, such as: 1, 2, 3")
    assigned_Agent: Literal["search_agent", "coder_agent", "file_agent", "memory_agent"] = Field(
        description="The name of the sub-agent responsible for this subtask"
    )
    task_description: str = Field(description="Command and description of the subtask given to the sub-agent and left right context")
    status: Literal["pending", "in progress", "completed", "failed"] = Field(
        default="pending", description="the current status of the subtask"
    )
    result: Optional[str] = Field(default=None, description="the results after subtask completion")

class ExecutionPlan(BaseModel):
    """main agent plans the overall plan"""
    original_goal: str = Field(description="Summerized version of the User's original needs and goals")
    subtasks: List[SubTask] = Field(description="Broken down list of subtasks and their sequence")
    current_task_index: int = Field(default=0, description="Indexes of the subtask in execution and next subtask")
    is_completed: bool = Field(default=False, description="Whether the entire task is fully completed")
    final_summary: Optional[str] = Field(default=None, description="Final response for user")