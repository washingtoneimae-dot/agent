from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.transaction import Transaction, TransactionType
from app.schemas import TokenPurchaseRequest, TokenPack

router = APIRouter()

TOKEN_PACKS = {
    "starter": TokenPack(id="starter", name="Starter", tokens=500, price_usd=4.99),
    "builder": TokenPack(id="builder", name="Builder", tokens=2000, price_usd=17.99),
    "pro": TokenPack(id="pro", name="Pro", tokens=10000, price_usd=79.99),
}


@router.get("/packs")
async def list_packs():
    return list(TOKEN_PACKS.values())


@router.get("/balance")
async def get_balance(user: User = Depends(get_current_user)):
    return {"balance": user.wallet_balance, "user_id": user.id}


@router.post("/purchase")
async def purchase_tokens(req: TokenPurchaseRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    pack = TOKEN_PACKS.get(req.pack)
    if not pack:
        raise HTTPException(status_code=400, detail=f"Invalid pack. Choose from: {', '.join(TOKEN_PACKS.keys())}")
    user.wallet_balance += pack.tokens
    db.add(user)
    db.add(Transaction(user_id=user.id, type=TransactionType.PURCHASE, amount=pack.tokens,
                       balance_after=user.wallet_balance, description=f"Purchased {pack.name} pack (${pack.price_usd:.2f})"))
    await db.commit()
    return {"success": True, "pack": pack.name, "tokens_added": pack.tokens, "new_balance": user.wallet_balance}


@router.get("/history")
async def get_history(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Transaction).where(Transaction.user_id == user.id).order_by(desc(Transaction.created_at)).limit(50))
    return [{"id": t.id, "type": t.type.value, "amount": t.amount, "description": t.description,
             "created_at": t.created_at.isoformat() if t.created_at else None} for t in result.scalars().all()]
