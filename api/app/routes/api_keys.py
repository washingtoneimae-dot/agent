import secrets, hashlib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.deps import get_current_user
from app.models.user import User
from app.models.api_key import ApiKey
from app.schemas import ApiKeyCreateRequest, ApiKeyResponse

router = APIRouter()


def generate_api_key() -> tuple:
    key = f"amk_{secrets.token_urlsafe(32)}"
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    key_prefix = key[:14]
    return key, key_hash, key_prefix


@router.post("", response_model=ApiKeyResponse, status_code=201)
async def create_api_key(req: ApiKeyCreateRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    full_key, key_hash, key_prefix = generate_api_key()
    api_key = ApiKey(user_id=user.id, name=req.name, key_prefix=key_prefix, key_hash=key_hash, scope=req.scope)
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)
    return ApiKeyResponse(id=api_key.id, name=api_key.name, key_prefix=api_key.key_prefix, scope=api_key.scope,
                          monthly_limit=api_key.monthly_limit, usage_count=api_key.usage_count,
                          is_active=api_key.is_active, created_at=api_key.created_at, full_key=full_key)


@router.get("", response_model=list[ApiKeyResponse])
async def list_api_keys(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApiKey).where(ApiKey.user_id == user.id, ApiKey.is_active == True))
    return [ApiKeyResponse(id=k.id, name=k.name, key_prefix=k.key_prefix, scope=k.scope,
                           monthly_limit=k.monthly_limit, usage_count=k.usage_count,
                           is_active=k.is_active, created_at=k.created_at) for k in result.scalars().all()]


@router.delete("/{key_id}")
async def revoke_api_key(key_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApiKey).where(ApiKey.id == key_id, ApiKey.user_id == user.id))
    key = result.scalar_one_or_none()
    if not key:
        raise HTTPException(status_code=404)
    key.is_active = False
    db.add(key)
    await db.commit()
    return {"success": True}
