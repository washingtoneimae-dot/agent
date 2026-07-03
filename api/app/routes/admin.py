from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.file import File, FileStatus
from app.models.api_key import ApiKey
from app.models.transaction import Transaction, TransactionType
from app.schemas import FileResponse

router = APIRouter()

async def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.get("/stats")
async def admin_stats(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    pending = (await db.execute(select(func.count(File.id)).where(File.status == FileStatus.PENDING))).scalar() or 0
    active = (await db.execute(select(func.count(File.id)).where(File.status == FileStatus.ACTIVE))).scalar() or 0
    total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
    verified = (await db.execute(select(func.count(User.id)).where(User.is_verified == True))).scalar() or 0
    total_txns = (await db.execute(select(func.count(Transaction.id)))).scalar() or 0
    total_revenue = (await db.execute(select(func.coalesce(func.sum(Transaction.amount), 0)).where(
        Transaction.type == TransactionType.PURCHASE))).scalar() or 0
    return {"files_pending": pending, "files_active": active, "total_users": total_users,
            "verified_admins": verified, "total_transactions": total_txns, "total_revenue_tokens": float(total_revenue)}


@router.get("/files", response_model=list[FileResponse])
async def list_all_files(status: str = None, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    query = select(File).order_by(desc(File.created_at))
    if status:
        try: query = query.where(File.status == FileStatus(status))
        except ValueError: pass
    result = await db.execute(query.limit(100))
    files = result.scalars().all()
    response = []
    for f in files:
        u = (await db.execute(select(User).where(User.id == f.contributor_id))).scalar_one_or_none()
        response.append(FileResponse(id=f.id, contributor_id=f.contributor_id, contributor_name=u.display_name if u else None,
            title=f.title, description=f.description[:200], category=f.category, product_tier=f.product_tier,
            tags=f.tags, price_tokens=f.price_tokens, rank_score=f.rank_score, download_count=f.download_count,
            status=f.status.value, file_size=f.file_size, created_at=f.created_at, updated_at=f.updated_at))
    return response


@router.get("/files/pending", response_model=list[FileResponse])
async def list_pending(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    return await list_all_files(status="pending", admin=admin, db=db)


@router.post("/files/{file_id}/approve")
async def approve_file(file_id: int, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    f = (await db.execute(select(File).where(File.id == file_id))).scalar_one_or_none()
    if not f: raise HTTPException(status_code=404)
    f.status = FileStatus.ACTIVE
    db.add(f)
    await db.commit()
    return {"success": True, "file_id": f.id, "title": f.title, "status": "active"}


@router.post("/files/{file_id}/reject")
async def reject_file(file_id: int, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    f = (await db.execute(select(File).where(File.id == file_id))).scalar_one_or_none()
    if not f: raise HTTPException(status_code=404)
    f.status = FileStatus.FLAGGED
    db.add(f)
    await db.commit()
    return {"success": True, "file_id": f.id, "status": "flagged"}


@router.get("/users")
async def list_users(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).order_by(desc(User.created_at)).limit(100))
    return [{"id": u.id, "email": u.email, "display_name": u.display_name, "wallet_balance": u.wallet_balance,
             "reputation_score": u.reputation_score, "is_verified": u.is_verified, "is_active": u.is_active,
             "created_at": u.created_at.isoformat() if u.created_at else None} for u in result.scalars().all()]


@router.post("/users/{user_id}/toggle-admin")
async def toggle_admin(user_id: int, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    if user_id == admin.id: raise HTTPException(status_code=400, detail="Cannot change your own status")
    u = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not u: raise HTTPException(status_code=404)
    u.is_verified = not u.is_verified
    db.add(u)
    await db.commit()
    return {"success": True, "user_id": u.id, "is_verified": u.is_verified}


@router.post("/users/{user_id}/deactivate")
async def deactivate_user(user_id: int, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    if user_id == admin.id: raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    u = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if not u: raise HTTPException(status_code=404)
    u.is_active = False
    db.add(u)
    await db.commit()
    return {"success": True, "user_id": u.id, "is_active": False}


@router.get("/api-keys")
async def list_all_api_keys(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApiKey, User.email, User.display_name).join(User, ApiKey.user_id == User.id).order_by(desc(ApiKey.created_at)).limit(100))
    return [{"id": k.ApiKey.id, "name": k.ApiKey.name, "key_prefix": k.ApiKey.key_prefix, "scope": k.ApiKey.scope,
             "usage_count": k.ApiKey.usage_count, "monthly_limit": k.ApiKey.monthly_limit,
             "is_active": k.ApiKey.is_active, "user_email": k.email, "user_name": k.display_name,
             "created_at": k.ApiKey.created_at.isoformat() if k.ApiKey.created_at else None} for k in result.all()]


@router.post("/api-keys/{key_id}/revoke")
async def revoke_api_key_global(key_id: int, admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    k = (await db.execute(select(ApiKey).where(ApiKey.id == key_id))).scalar_one_or_none()
    if not k: raise HTTPException(status_code=404)
    k.is_active = False
    db.add(k)
    await db.commit()
    return {"success": True}


@router.get("/settings")
async def get_settings(admin: User = Depends(require_admin)):
    from app.config import settings
    return {"ai_provider": settings.ai_provider, "ai_model": settings.ai_model or "auto",
            "domain": settings.domain,
            "stripe_configured": bool(settings.stripe_secret_key and not settings.stripe_secret_key.startswith("sk_test_")),
            "debug": settings.debug}


@router.get("/transactions")
async def list_transactions(admin: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Transaction, User.email).join(User, Transaction.user_id == User.id).order_by(desc(Transaction.created_at)).limit(100))
    return [{"id": t.Transaction.id, "user_email": t.email, "type": t.Transaction.type.value,
             "amount": t.Transaction.amount, "description": t.Transaction.description,
             "created_at": t.Transaction.created_at.isoformat() if t.Transaction.created_at else None} for t in result.all()]
