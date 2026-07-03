from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.file import File, FileCategory, FileProductTier, FileStatus
from app.models.transaction import Transaction, TransactionType
from app.schemas import FileCreateRequest, FileResponse

router = APIRouter()


@router.get("", response_model=list[FileResponse])
async def list_files(
    category: FileCategory = None,
    tier: FileProductTier = None,
    sort: str = Query("rank", regex="^(rank|price|newest|downloads)$"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(File).where(File.status == FileStatus.ACTIVE)
    if category:
        query = query.where(File.category == category)
    if tier:
        query = query.where(File.product_tier == tier)
    sort_map = {"rank": desc(File.rank_score), "price": File.price_tokens, "newest": desc(File.created_at), "downloads": desc(File.download_count)}
    query = query.order_by(sort_map.get(sort, desc(File.rank_score))).offset(offset).limit(limit)
    result = await db.execute(query)
    files = result.scalars().all()
    response = []
    for f in files:
        u = (await db.execute(select(User).where(User.id == f.contributor_id))).scalar_one_or_none()
        response.append(FileResponse(
            id=f.id, contributor_id=f.contributor_id, contributor_name=u.display_name if u else None,
            title=f.title, description=f.description[:200] + ("..." if len(f.description) > 200 else ""),
            category=f.category, product_tier=f.product_tier, tags=f.tags, price_tokens=f.price_tokens,
            rank_score=f.rank_score, download_count=f.download_count, status=f.status.value,
            file_size=f.file_size, created_at=f.created_at, updated_at=f.updated_at,
        ))
    return response


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(file_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(File).where(File.id == file_id))
    f = result.scalar_one_or_none()
    if not f:
        raise HTTPException(status_code=404)
    u = (await db.execute(select(User).where(User.id == f.contributor_id))).scalar_one_or_none()
    return FileResponse(
        id=f.id, contributor_id=f.contributor_id, contributor_name=u.display_name if u else None,
        title=f.title, description=f.description, category=f.category, product_tier=f.product_tier,
        tags=f.tags, price_tokens=f.price_tokens, rank_score=f.rank_score,
        download_count=f.download_count, status=f.status.value, file_size=f.file_size,
        created_at=f.created_at, updated_at=f.updated_at,
    )


@router.post("", response_model=FileResponse, status_code=201)
async def upload_file(req: FileCreateRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    f = File(contributor_id=user.id, title=req.title, description=req.description,
             category=req.category, product_tier=req.product_tier, tags=req.tags,
             price_tokens=req.price_tokens, status=FileStatus.PENDING)
    db.add(f)
    await db.commit()
    await db.refresh(f)
    return FileResponse(
        id=f.id, contributor_id=f.contributor_id, contributor_name=user.display_name,
        title=f.title, description=f.description, category=f.category, product_tier=f.product_tier,
        tags=f.tags, price_tokens=f.price_tokens, rank_score=f.rank_score,
        download_count=f.download_count, status=f.status.value, file_size=f.file_size,
        created_at=f.created_at, updated_at=f.updated_at,
    )


@router.post("/{file_id}/download")
async def download_file(file_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(File).where(File.id == file_id))
    f = result.scalar_one_or_none()
    if not f:
        raise HTTPException(status_code=404)
    if f.status != FileStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="File is not available for download")
    if user.wallet_balance < f.price_tokens:
        raise HTTPException(status_code=402, detail="Insufficient tokens")
    user.wallet_balance -= f.price_tokens
    db.add(user)
    c_result = await db.execute(select(User).where(User.id == f.contributor_id))
    contributor = c_result.scalar_one_or_none()
    if contributor:
        c_amount = f.price_tokens * 0.7
        contributor.wallet_balance += c_amount
        db.add(contributor)
        db.add(Transaction(user_id=contributor.id, file_id=f.id, type=TransactionType.EARN, amount=c_amount,
                           description=f"Earned from download of '{f.title}'"))
    db.add(Transaction(user_id=user.id, file_id=f.id, type=TransactionType.DOWNLOAD, amount=-f.price_tokens,
                       description=f"Downloaded '{f.title}'"))
    f.download_count += 1
    db.add(f)
    await db.commit()
    return {"success": True, "file_id": f.id, "title": f.title, "tokens_spent": f.price_tokens}
