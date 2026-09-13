"""
Network metric service - business logic for metric operations.
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta

from database.models import NetworkMetric
from schemas.metric import NetworkMetricCreate


class MetricService:
    """Service class for network metric operations."""

    @staticmethod
    def create_metric(db: Session, metric_data: NetworkMetricCreate) -> NetworkMetric:
        """
        Create a new network metric record.

        Args:
            db: Database session
            metric_data: Metric creation data

        Returns:
            Created NetworkMetric object
        """
        metric = NetworkMetric(
            timestamp=metric_data.timestamp,
            flows_per_second=metric_data.flows_per_second,
            packets_per_second=metric_data.packets_per_second,
            bytes_per_second=metric_data.bytes_per_second,
            tcp_percentage=metric_data.tcp_percentage,
            udp_percentage=metric_data.udp_percentage,
            dns_percentage=metric_data.dns_percentage
        )

        db.add(metric)
        db.commit()
        db.refresh(metric)

        return metric

    @staticmethod
    def get_current_metric(db: Session) -> Optional[NetworkMetric]:
        """
        Get the most recent network metric.

        Args:
            db: Database session

        Returns:
            Most recent NetworkMetric or None
        """
        return db.query(NetworkMetric).order_by(desc(NetworkMetric.timestamp)).first()

    @staticmethod
    def get_metrics_history(
        db: Session,
        hours: int = 24,
        limit: int = 100
    ) -> tuple[List[NetworkMetric], int]:
        """
        Get network metrics for the specified time period.

        Args:
            db: Database session
            hours: Number of hours of history to retrieve
            limit: Maximum number of records to return

        Returns:
            Tuple of (metrics list, total count)
        """
        since = datetime.utcnow() - timedelta(hours=hours)

        query = db.query(NetworkMetric).filter(NetworkMetric.timestamp >= since)

        total = query.count()
        metrics = query.order_by(desc(NetworkMetric.timestamp)).limit(limit).all()

        return metrics, total

    @staticmethod
    def get_average_flow_rate(db: Session, hours: int = 1) -> float:
        """
        Calculate average flow rate for the specified period.

        Args:
            db: Database session
            hours: Number of hours to average over

        Returns:
            Average flows per second
        """
        from sqlalchemy import func

        since = datetime.utcnow() - timedelta(hours=hours)

        result = db.query(
            func.avg(NetworkMetric.flows_per_second)
        ).filter(
            NetworkMetric.timestamp >= since
        ).scalar()

        return result if result else 0.0
