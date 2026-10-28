from typing import Literal
from pydantic import BaseModel, Field

class TaskRequest(BaseModel):
    task: str = Field(min_length=5, max_length=500)
    operation: Literal["sales_report"]
    input_file: str = Field(pattern=r"^[A-Za-z0-9_.-]+\.csv$", max_length=100)
    output_file: str = Field(pattern=r"^[A-Za-z0-9_.-]+\.json$", max_length=100)
    max_retries: int = Field(default=1, ge=0, le=2)

class TaskCreated(BaseModel):
    task_id: str
    status: str
    message: str
