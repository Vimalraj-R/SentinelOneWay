"""
Pydantic schemas for Asset API endpoints.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class AssetCriticality(str, Enum):
    """Asset criticality enumeration."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class AssetBase(BaseModel):
    """Base asset schema."""
    ip_address: str
    hostname: str
    asset_type: str
    criticality: AssetCriticality
    risk_score: int = Field(ge=0, le=100, default=0)


class AssetCreate(AssetBase):
    """Schema for creating a new asset."""
    pass


class AssetResponse(AssetBase):
    """Schema for asset API responses."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AssetListResponse(BaseModel):
    """Schema for asset list responses."""
    total: int
    assets: list[AssetResponse]


# Import Optional for type hints
from typing import Optional
