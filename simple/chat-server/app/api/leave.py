from fastapi import APIRouter
from app.models.leave import LeaveRequest

router = APIRouter()

@router.post("/leave/submit")
async def submit_leave(request: LeaveRequest):
    """请假提交接口"""
    print(f"收到完整请假申请: {request}")
    
    # 验证逻辑
    if not request.applicant or not request.start_time or not request.end_time:
        return {"success": False, "message": "请假人、开始时间和结束时间不能为空"}
    
    return {
        "success": True, 
        "message": f"✅ 申请已提交！已成功为 {request.applicant} 办理了从 {request.start_time} 到 {request.end_time} 的 {request.leave_type}。"
    }
