import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.transaction import Transaction, TransactionType
from app.config import settings

router = APIRouter()

TOKEN_PACKS = {
    "starter": {"name": "Starter", "tokens": 500, "price_cents": 499},
    "builder": {"name": "Builder", "tokens": 2000, "price_cents": 1799},
    "pro": {"name": "Pro", "tokens": 10000, "price_cents": 7999},
}

stripe.api_key = settings.stripe_secret_key


@router.post("/create-checkout")
async def create_checkout(pack_id: str = "builder", user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    pack = TOKEN_PACKS.get(pack_id)
    if not pack:
        raise HTTPException(status_code=400, detail=f"Invalid pack. Choose: {', '.join(TOKEN_PACKS.keys())}")

    # Demo mode if no Stripe key
    if not settings.stripe_secret_key or settings.stripe_secret_key.startswith("sk_test_"):
        user.wallet_balance += pack["tokens"]
        db.add(user)
        db.add(Transaction(user_id=user.id, type=TransactionType.PURCHASE, amount=pack["tokens"],
                           balance_after=user.wallet_balance,
                           description=f"Purchased {pack['name']} pack (${pack['price_cents']/100:.2f}) — demo"))
        await db.commit()
        return {"mock": True, "success": True, "pack": pack["name"], "tokens_added": pack["tokens"], "new_balance": user.wallet_balance}

    # Real Stripe
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price_data": {"currency": "usd",
                         "product_data": {"name": f"AgentMarket {pack['name']} — {pack['tokens']} tokens"},
                         "unit_amount": pack["price_cents"]}, "quantity": 1}],
            mode="payment",
            metadata={"pack_id": pack_id, "user_id": str(user.id), "tokens": str(pack["tokens"])},
            success_url=f"{settings.domain}/dashboard?payment=success",
            cancel_url=f"{settings.domain}/dashboard?payment=cancel",
        )
        return {"checkout_url": session.url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    if not sig_header or not settings.stripe_webhook_secret:
        return {"received": True}
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    if event["type"] == "checkout.session.completed":
        async for db in get_db():
            await _handle_checkout(event["data"]["object"], db)
    return {"received": True}


async def _handle_checkout(session: dict, db: AsyncSession):
    metadata = session.get("metadata", {})
    user_id = int(metadata.get("user_id", 0))
    tokens = int(metadata.get("tokens", 0))
    pack_id = metadata.get("pack_id", "unknown")
    if not user_id or not tokens:
        return
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return
    existing = await db.execute(select(Transaction).where(
        Transaction.reference_id == session.get("id"), Transaction.type == TransactionType.PURCHASE))
    if existing.scalar_one_or_none():
        return
    user.wallet_balance += tokens
    db.add(user)
    db.add(Transaction(user_id=user.id, type=TransactionType.PURCHASE, amount=tokens,
                       balance_after=user.wallet_balance, description=f"Stripe purchase: {pack_id} pack",
                       reference_id=session.get("id")))
    await db.commit()
