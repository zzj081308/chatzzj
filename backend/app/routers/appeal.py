from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies import get_current_user, get_current_admin
from app.models.user import User
from app.schemas.appeal import AppealSubmit, AppealResponse, AdminAppealAction
from app.services import appeal_service

router = APIRouter(prefix="/api/v1/appeals", tags=["appeals"])


@router.post("/check")
async def check_account(body: AppealSubmit, db: AsyncSession = Depends(get_db)):
    result = await appeal_service.check_account(db, body.username, body.password)
    return result


@router.post("/submit", response_model=AppealResponse, status_code=201)
async def submit_appeal(body: AppealSubmit, db: AsyncSession = Depends(get_db)):
    appeal = await appeal_service.submit_appeal(db, body.username, body.password, body.reason)
    return AppealResponse.model_validate(appeal)


@router.get("/my", response_model=list[AppealResponse])
async def get_my_appeals(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    appeals = await appeal_service.get_user_appeals(db, current_user.id)
    return [AppealResponse.model_validate(a) for a in appeals]


@router.get("/admin/all", response_model=list[AppealResponse])
async def admin_get_appeals(
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    appeals = await appeal_service.get_all_appeals(db, status)
    return [AppealResponse.model_validate(a) for a in appeals]


@router.patch("/admin/{appeal_id}/approve", response_model=AppealResponse)
async def admin_approve_appeal(
    appeal_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    appeal = await appeal_service.approve_appeal(db, appeal_id, admin.id)
    return AppealResponse.model_validate(appeal)


@router.patch("/admin/{appeal_id}/reject", response_model=AppealResponse)
async def admin_reject_appeal(
    appeal_id: int,
    body: AdminAppealAction,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    if not body.response:
        raise HTTPException(status_code=400, detail="拒绝原因不能为空")
    appeal = await appeal_service.reject_appeal(db, appeal_id, admin.id, body.response)
    return AppealResponse.model_validate(appeal)


@router.post("/my-appeals", response_model=list[AppealResponse])
async def get_my_appeals_noauth(body: AppealSubmit, db: AsyncSession = Depends(get_db)):
    from app.utils.security import verify_password
    r = await db.execute(select(User).where(User.username == body.username))
    u = r.scalar_one_or_none()
    if not u:
        raise HTTPException(status_code=400, detail="账号不存在")
    if not verify_password(body.password, u.hashed_password):
        raise HTTPException(status_code=400, detail="密码错误")
    appeals = await appeal_service.get_user_appeals(db, u.id)
    return [AppealResponse.model_validate(a) for a in appeals]
