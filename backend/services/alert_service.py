"""
Alert service - business logic for alert operations.
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
import logging

from database.models import Alert, AlertStatus, AlertSeverity
from schemas.alert import AlertCreate, AlertUpdate
from websocket.manager import manager

logger = logging.getLogger(__name__)


class AlertService:
    """Service class for alert-related operations."""

    @staticmethod
    def get_alerts(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        severity: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List[Alert], int]:
        """
        Retrieve alerts with optional filtering.

        Args:
            db: Database session
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            severity: Filter by severity (optional)
            status: Filter by status (optional)

        Returns:
            Tuple of (alerts list, total count)
        """
        query = db.query(Alert)

        # Apply filters
        if severity:
            query = query.filter(Alert.severity == severity)
        if status:
            query = query.filter(Alert.status == status)

        # Get total count before pagination
        total = query.count()

        # Apply ordering and pagination
        alerts = query.order_by(desc(Alert.timestamp)).offset(skip).limit(limit).all()

        return alerts, total

    @staticmethod
    def get_alert_by_id(db: Session, alert_id: int) -> Optional[Alert]:
        """
        Retrieve a single alert by ID.

        Args:
            db: Database session
            alert_id: Alert ID

        Returns:
            Alert object or None if not found
        """
        return db.query(Alert).filter(Alert.id == alert_id).first()

    @staticmethod
    def create_alert(db: Session, alert_data: AlertCreate) -> Alert:
        """
        Create a new alert.

        Args:
            db: Database session
            alert_data: Alert creation data

        Returns:
            Created Alert object
        """
        alert = Alert(
            timestamp=alert_data.timestamp,
            flow_id=alert_data.flow_id,
            threat_class=alert_data.threat_class,
            severity=alert_data.severity,
            confidence=alert_data.confidence,
            risk_score=alert_data.risk_score,
            src_ip=alert_data.src_ip,
            dst_ip=alert_data.dst_ip,
            src_port=alert_data.src_port,
            dst_port=alert_data.dst_port,
            protocol=alert_data.protocol,
            status=alert_data.status,
            evidence_json=alert_data.evidence_json
        )

        db.add(alert)
        db.commit()
        db.refresh(alert)

        return alert

    @staticmethod
    def update_alert_status(
        db: Session,
        alert_id: int,
        status_data: AlertUpdate
    ) -> Optional[Alert]:
        """
        Update alert status.

        Args:
            db: Database session
            alert_id: Alert ID
            status_data: Status update data

        Returns:
            Updated Alert object or None if not found
        """
        alert = db.query(Alert).filter(Alert.id == alert_id).first()

        if not alert:
            return None

        alert.status = status_data.status
        db.commit()
        db.refresh(alert)

        return alert

    @staticmethod
    def get_recent_alerts(db: Session, limit: int = 6) -> List[Alert]:
        """
        Get most recent alerts for dashboard.

        Args:
            db: Database session
            limit: Maximum number of alerts to return

        Returns:
            List of recent alerts
        """
        return db.query(Alert).order_by(desc(Alert.timestamp)).limit(limit).all()

    @staticmethod
    def get_alert_counts_by_severity(db: Session) -> dict:
        """
        Get alert counts grouped by severity.

        Args:
            db: Database session

        Returns:
            Dictionary with severity counts
        """
        from sqlalchemy import func

        results = db.query(
            Alert.severity,
            func.count(Alert.id)
        ).group_by(Alert.severity).all()

        return {severity.value: count for severity, count in results}

    @staticmethod
    def get_alert_counts_by_status(db: Session) -> dict:
        """
        Get alert counts grouped by status.

        Args:
            db: Database session

        Returns:
            Dictionary with status counts
        """
        from sqlalchemy import func

        results = db.query(
            Alert.status,
            func.count(Alert.id)
        ).group_by(Alert.status).all()

        return {status.value: count for status, count in results}

    @staticmethod
    def get_active_alert_count(db: Session) -> int:
        """
        Get count of active alerts.

        Args:
            db: Database session

        Returns:
            Number of active alerts
        """
        return db.query(Alert).filter(Alert.status == AlertStatus.ACTIVE).count()

    @staticmethod
    def get_critical_threat_count(db: Session) -> int:
        """
        Get count of critical threats.

        Args:
            db: Database session

        Returns:
            Number of critical severity alerts
        """
        from database.models import AlertSeverity

        return db.query(Alert).filter(
            Alert.severity == AlertSeverity.CRITICAL,
            Alert.status.in_([AlertStatus.ACTIVE, AlertStatus.INVESTIGATING])
        ).count()

    @staticmethod
    async def create_alert_with_broadcast(
        db: Session,
        detection_result: Dict[str, Any],
        flow_data: Dict[str, Any],
        features: Optional[Dict[str, float]] = None
    ) -> Alert:
        """
        Create alert from detection result and broadcast to WebSocket clients.

        Args:
            db: Database session
            detection_result: Output from hybrid detection engine
            flow_data: Network flow information (IPs, ports, protocol)
            features: Original features used for detection (for explainability)

        Returns:
            Created Alert object
        """
        try:
            # Convert severity string to enum
            severity_map = {
                'critical': AlertSeverity.CRITICAL,
                'high': AlertSeverity.HIGH,
                'medium': AlertSeverity.MEDIUM,
                'low': AlertSeverity.LOW
            }
            severity = severity_map.get(
                detection_result['severity'].lower(),
                AlertSeverity.MEDIUM
            )

            # Create alert object
            alert = Alert(
                timestamp=datetime.utcnow(),
                flow_id=flow_data.get('flow_id', f"flow_{datetime.utcnow().timestamp()}"),

                # Threat information
                threat_class=detection_result['threat_class'],
                severity=severity,
                confidence=detection_result['confidence'],
                risk_score=detection_result['risk_score'],

                # Network information
                src_ip=flow_data.get('src_ip', 'unknown'),
                dst_ip=flow_data.get('dst_ip', 'unknown'),
                src_port=str(flow_data.get('src_port', '')),
                dst_port=str(flow_data.get('dst_port', 'unknown')),
                protocol=flow_data.get('protocol', 'unknown'),

                # Evidence (include features for explainability)
                evidence_json=json.dumps({
                    'evidence': detection_result.get('evidence', {}),
                    'human_explanation': detection_result.get('human_explanation', []),
                    'detectors_triggered': detection_result.get('detectors_triggered', []),
                    'anomaly_score': detection_result.get('anomaly_score', 0),
                    'features': features or {}  # Store features for explanation
                }),

                # Status
                status=AlertStatus.ACTIVE
            )

            # Save to database
            db.add(alert)
            db.commit()
            db.refresh(alert)

            logger.info(
                f"Alert created: {alert.threat_class} from {alert.src_ip} "
                f"(severity: {alert.severity}, risk: {alert.risk_score})"
            )

            # Broadcast to WebSocket clients
            await AlertService._broadcast_alert(alert, detection_result)

            return alert

        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            db.rollback()
            raise

    @staticmethod
    async def _broadcast_alert(alert: Alert, detection_result: Dict[str, Any]):
        """
        Broadcast alert to all connected WebSocket clients.

        Args:
            alert: Alert database object
            detection_result: Full detection result for additional context
        """
        # Parse evidence JSON
        try:
            evidence = json.loads(alert.evidence_json) if alert.evidence_json else {}
        except json.JSONDecodeError:
            evidence = {}

        # Prepare alert data for broadcast
        alert_data = {
            'id': alert.id,
            'timestamp': alert.timestamp.isoformat() if alert.timestamp else None,
            'flow_id': alert.flow_id,

            # Threat information
            'threat_class': alert.threat_class,
            'severity': alert.severity.value if isinstance(alert.severity, AlertSeverity) else alert.severity,
            'confidence': alert.confidence,
            'risk_score': alert.risk_score,

            # Network information
            'src_ip': alert.src_ip,
            'dst_ip': alert.dst_ip,
            'src_port': alert.src_port,
            'dst_port': alert.dst_port,
            'protocol': alert.protocol,

            # Investigation
            'status': alert.status.value if isinstance(alert.status, AlertStatus) else alert.status,

            # Evidence (first explanation only for notification)
            'explanation': evidence.get('human_explanation', [''])[0] if evidence.get('human_explanation') else '',
            'detectors_triggered': evidence.get('detectors_triggered', []),
            'anomaly_score': evidence.get('anomaly_score', 0),

            # Additional context
            'created_at': alert.created_at.isoformat() if alert.created_at else None
        }

        # Broadcast to all connected clients
        await manager.broadcast_alert(alert_data)

        logger.info(
            f"Alert broadcast to {len(manager.active_connections)} clients: "
            f"{alert.threat_class} (risk: {alert.risk_score})"
        )
