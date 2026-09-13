"""
Asset API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database.base import get_db
from schemas.asset import AssetResponse, AssetListResponse
from services.asset_service import AssetService

router = APIRouter(prefix="/api/assets", tags=["assets"])


@router.get("", response_model=AssetListResponse)
def get_assets(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of network assets.

    Returns information about monitored assets including:
    - Hostname and IP address
    - Asset type (server, workstation, network device)
    - Criticality level
    - Current risk score

    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return (max 1000)
    """
    assets, total = AssetService.get_assets(
        db=db,
        skip=skip,
        limit=limit
    )

    return AssetListResponse(
        total=total,
        assets=assets
    )


@router.get("/{asset_id}", response_model=AssetResponse)
def get_asset(
    asset_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific asset by ID.

    - **asset_id**: The ID of the asset to retrieve
    """
    asset = AssetService.get_asset_by_id(db=db, asset_id=asset_id)

    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    return asset
