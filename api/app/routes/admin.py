from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.file import File, FileStatus
from app.schemas import FileResponse

router = APIRouter()


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/files/pending", response_model=list[FileResponse])
async def list_pending(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(File).where(File.status == FileStatus.PENDING).order_by(File.created_at.desc()))
    files = result.scalars().all()
    response = []
    for f in files:
        u = (await db.execute(select(User).where(User.id == f.contributor_id))).scalar_one_or_none()
        response.append(FileResponse(
            id=f.id, contributor_id=f.contributor_id, contributor_name=u.display_name if u else None,
            title=f.title, description=f.description[:200], category=f.category, product_tier=f.product_tier,
            tags=f.tags, price_tokens=f.price_tokens, rank_score=f.rank_score,
            download_count=f.download_count, status=f.status.value, file_size=f.file_size,
            created_at=f.created_at, updated_at=f.updated_at,
        ))
    return response


@router.post("/files/{file_id}/approve")
async def approve_file(file_id: int, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(File).where(File.id == file_id))
    f = result.scalar_one_or_none()
    if not f:
        raise HTTPException(status_code=404)
    if f.status != FileStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"File is {f.status.value}, not pending")
    f.status = FileStatus.ACTIVE
    db.add(f)
    await db.commit()
    return {"success": True, "file_id": f.id, "title": f.title, "status": "active"}


@router.post("/files/{file_id}/reject")
async def reject_file(file_id: int, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(File).where(File.id == file_id))
    f = result.scalar_one_or_none()
    if not f:
        raise HTTPException(status_code=404)
    f.status = FileStatus.FLAGGED
    db.add(f)
    await db.commit()
    return {"success": True, "file_id": f.id, "status": "flagged"}


@router.get("/stats")
async def admin_stats(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    pending = await db.execute(select(func.count(File.id)).where(File.status == FileStatus.PENDING))
    active = await db.execute(select(func.count(File.id)).where(File.status == FileStatus.ACTIVE))
    total_users = await db.execute(select(func.count(User.id)))
    return {
        "files_pending": pending.scalar() or 0,
        "files_active": active.scalar() or 0,
        "total_users": total_users.scalar() or 0,
    }
