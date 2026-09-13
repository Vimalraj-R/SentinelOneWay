"""
Asset service - business logic for asset operations.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional

from database.models import Asset, Alert, AlertStatus
from schemas.asset import AssetCreate


class AssetService:
    """Service class for asset-related operations."""

    @staticmethod
    def get_assets(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Asset], int]:
        """
        Retrieve all assets with pagination.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            Tuple of (assets list, total count)
        """
        query = db.query(Asset)

        total = query.count()
        assets = query.order_by(Asset.hostname).offset(skip).limit(limit).all()

        return assets, total

    @staticmethod
    def get_asset_by_id(db: Session, asset_id: int) -> Optional[Asset]:
        """
        Retrieve a single asset by ID.

        Args:
            db: Database session
            asset_id: Asset ID

        Returns:
            Asset object or None if not found
        """
        return db.query(Asset).filter(Asset.id == asset_id).first()

    @staticmethod
    def get_asset_by_ip(db: Session, ip_address: str) -> Optional[Asset]:
        """
        Retrieve a single asset by IP address.

        Args:
            db: Database session
            ip_address: IP address

        Returns:
            Asset object or None if not found
        """
        return db.query(Asset).filter(Asset.ip_address == ip_address).first()

    @staticmethod
    def create_asset(db: Session, asset_data: AssetCreate) -> Asset:
        """
        Create a new asset.

        Args:
            db: Database session
            asset_data: Asset creation data

        Returns:
            Created Asset object
        """
        asset = Asset(
            ip_address=asset_data.ip_address,
            hostname=asset_data.hostname,
            asset_type=asset_data.asset_type,
            criticality=asset_data.criticality,
            risk_score=asset_data.risk_score
        )

        db.add(asset)
        db.commit()
        db.refresh(asset)

        return asset

    @staticmethod
    def get_top_threatened_assets(db: Session, limit: int = 5) -> List[dict]:
        """
        Get assets with the most active alerts.

        Args:
            db: Database session
            limit: Maximum number of assets to return

        Returns:
            List of dictionaries with asset info and alert count
        """
        # Count alerts per destination IP (targeted asset)
        alert_counts = db.query(
            Alert.dst_ip,
            func.count(Alert.id).label('alert_count')
        ).filter(
            Alert.status.in_([AlertStatus.ACTIVE, AlertStatus.INVESTIGATING])
        ).group_by(
            Alert.dst_ip
        ).order_by(
            desc('alert_count')
        ).limit(limit).all()

        # Get asset details for each IP
        results = []
        for dst_ip, alert_count in alert_counts:
            asset = db.query(Asset).filter(Asset.ip_address == dst_ip).first()

            if asset:
                results.append({
                    'hostname': asset.hostname,
                    'ip': asset.ip_address,
                    'alerts': alert_count,
                    'risk': asset.criticality.value
                })
            else:
                # Asset not in database, use IP only
                results.append({
                    'hostname': f'unknown-{dst_ip}',
                    'ip': dst_ip,
                    'alerts': alert_count,
                    'risk': 'Unknown'
                })

        return results

    @staticmethod
    def update_asset_risk_scores(db: Session):
        """
        Update risk scores for all assets based on recent alerts.

        This would be called periodically to recalculate risk scores.
        For now, it's a placeholder for future implementation.

        Args:
            db: Database session
        """
        # TODO: Implement risk score calculation logic
        pass
