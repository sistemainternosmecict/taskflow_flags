from typing import Optional
from pydantic import BaseModel
from domain.enum import FlagStatusEnum

class CreateFlag(BaseModel):
    tb_flags_task_id: str
    tb_flags_task_user_id: str


class CreateFlagResponse(BaseModel):
    tb_flags_id: int
    tb_flags_created_at: str 
    tb_flags_status: FlagStatusEnum


class FlagResponse(BaseModel):
    tb_flags_id: int
    tb_flags_created_at: str
    tb_flags_task_id: str
    tb_flags_task_user_id: str
    tb_flags_status: FlagStatusEnum
    tb_flags_updated_at: Optional[str] = None


class UpdateFlagStatus(BaseModel):
    tb_flags_task_id: str
    tb_flags_status: FlagStatusEnum


class UpdateFlagResponse(BaseModel):
    tb_flags_status: FlagStatusEnum
    tb_updated_at: str 


class TaskBatchRequest(BaseModel):
    task_ids: list[str]
