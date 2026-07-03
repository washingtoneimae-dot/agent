from pydantic import BaseModel, Field
from typing import Optional, Any
from app.models.file import FileCategory, FileProductTier


class RegisterRequest(BaseModel):
    email: str = Field(..., max_length=255)
    password: str = Field(..., min_length=6, max_length=128)
    display_name: Optional[str] = Field(None, max_length=100)


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    email: str
    display_name: Optional[str]
    wallet_balance: float
    reputation_score: float
    is_verified: bool
    created_at: Any

    class Config:
        from_attributes = True


class FileCreateRequest(BaseModel):
    title: str = Field(..., max_length=200)
    description: str
    category: FileCategory
    product_tier: FileProductTier = FileProductTier.SKILL_CREATION_FILE
    tags: Optional[str] = ""
    price_tokens: int = Field(100, ge=0)


class FileResponse(BaseModel):
    id: int
    contributor_id: int
    contributor_name: Optional[str] = None
    title: str
    description: str
    category: FileCategory
    product_tier: FileProductTier
    tags: Optional[str]
    price_tokens: int
    rank_score: float
    download_count: int
    status: str
    file_size: int
    created_at: Any
    updated_at: Any

    class Config:
        from_attributes = True


class TokenPurchaseRequest(BaseModel):
    pack: str


class TokenPack(BaseModel):
    id: str
    name: str
    tokens: int
    price_usd: float


class ReviewCreateRequest(BaseModel):
    file_id: int
    score: int = Field(..., ge=1, le=5)
    review_text: Optional[str] = ""
    agent_used: Optional[str] = None
    use_case: Optional[str] = None
    synthesis_rounds: Optional[str] = None
    paired_file_ids: Optional[str] = None


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    file_id: int
    score: int
    review_text: Optional[str]
    agent_used: Optional[str]
    use_case: Optional[str]
    synthesis_rounds: Optional[str]
    paired_file_ids: Optional[str]
    created_at: Any

    class Config:
        from_attributes = True


class ReviewSummaryResponse(BaseModel):
    file_id: int
    summary_json: dict
    total_reviews: int
    avg_score: float
    generated_at: Any
    updated_at: Any


class ApiKeyCreateRequest(BaseModel):
    name: str = Field(..., max_length=100)
    scope: str = "read:files"


class ApiKeyResponse(BaseModel):
    id: int
    name: str
    key_prefix: str
    scope: str
    monthly_limit: int
    usage_count: int
    is_active: bool
    created_at: Any
    full_key: Optional[str] = None

    class Config:
        from_attributes = True
