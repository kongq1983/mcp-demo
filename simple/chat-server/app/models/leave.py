from pydantic import BaseModel
from typing import Optional

class LeaveRequest(BaseModel):
    applicant: str          # 请假人
    start_time: str         # 请假开始时间
    end_time: str           # 请假结束时间
    leave_type: str         # 请假类型
    reason: str             # 原因

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []
