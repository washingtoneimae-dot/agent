from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.rating import Rating
from app.models.review_summary import ReviewSummary
from app.models.file import File
from app.models.transaction import Transaction
from app.schemas import ReviewCreateRequest, ReviewResponse, ReviewSummaryResponse
from app.services.ai import generate_review_summary

router = APIRouter()


@router.post("", response_model=ReviewResponse, status_code=201)
async def create_review(req: ReviewCreateRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    txn = (await db.execute(select(Transaction).where(Transaction.user_id == user.id, Transaction.file_id == req.file_id))).scalar_one_or_none()
    review = Rating(user_id=user.id, file_id=req.file_id, score=req.score, review_text=req.review_text,
                    agent_used=req.agent_used, use_case=req.use_case, synthesis_rounds=req.synthesis_rounds,
                    paired_file_ids=req.paired_file_ids, verified_download=txn is not None)
    db.add(review)
    await db.commit()
    await db.refresh(review)
    await _regenerate_summary(req.file_id, db)
    return review


@router.get("/{file_id}", response_model=list[ReviewResponse])
async def get_reviews(file_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Rating).where(Rating.file_id == file_id).order_by(desc(Rating.created_at)).limit(50))
    return result.scalars().all()


@router.get("/{file_id}/summary", response_model=ReviewSummaryResponse)
async def get_summary(file_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ReviewSummary).where(ReviewSummary.file_id == file_id))
    summary = result.scalar_one_or_none()
    if not summary:
        return ReviewSummaryResponse(file_id=file_id, summary_json={"note": "Not enough reviews yet"},
                                      total_reviews=0, avg_score=0.0, generated_at=None, updated_at=None)
    return summary


@router.post("/{file_id}/summary")
async def store_summary(file_id: int, payload: dict, db: AsyncSession = Depends(get_db)):
    await _save_summary(file_id, payload, db)
    return {"success": True}


@router.post("/{file_id}/regenerate")
async def regenerate_summary(file_id: int, db: AsyncSession = Depends(get_db)):
    result = await _regenerate_summary(file_id, db)
    if result is None:
        return {"success": False, "note": "Not enough reviews to generate summary", "file_id": file_id}
    return {"success": True, "file_id": file_id, "summary": result}


async def _regenerate_summary(file_id: int, db: AsyncSession):
    review_result = await db.execute(select(Rating).where(Rating.file_id == file_id).limit(50))
    reviews = review_result.scalars().all()
    if len(reviews) < 1:
        return None
    file_result = await db.execute(select(File).where(File.id == file_id))
    file = file_result.scalar_one_or_none()
    if not file:
        return None
    review_data = [{"score": r.score, "text": r.review_text or "", "agent": r.agent_used or "unknown",
                    "use_case": r.use_case or "unknown", "synthesis_rounds": r.synthesis_rounds or "unknown"} for r in reviews]
    summary_data = await generate_review_summary(
        title=file.title, category=file.category.value if hasattr(file.category, 'value') else str(file.category),
        reviews=review_data)
    if not summary_data:
        return None
    await _save_summary(file_id, summary_data, db)
    return summary_data


async def _save_summary(file_id: int, payload: dict, db: AsyncSession):
    result = await db.execute(select(ReviewSummary).where(ReviewSummary.file_id == file_id))
    summary = result.scalar_one_or_none()
    score_result = await db.execute(select(func.avg(Rating.score), func.count(Rating.id)).where(Rating.file_id == file_id))
    avg_score, total_reviews = score_result.one()
    if summary:
        summary.summary_json = payload
        summary.total_reviews = total_reviews or 0
        summary.avg_score = float(avg_score or 0.0)
    else:
        summary = ReviewSummary(file_id=file_id, summary_json=payload, total_reviews=total_reviews or 0, avg_score=float(avg_score or 0.0))
        db.add(summary)
    await db.commit()
    await db.refresh(summary)
    return summary
