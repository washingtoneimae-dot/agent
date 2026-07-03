from fastapi import APIRouter, Depends
from app.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/whoami")
async def whoami(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "display_name": user.display_name,
        "wallet_balance": user.wallet_balance,
        "is_verified": user.is_verified,
    }
