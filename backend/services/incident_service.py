"""
Incident service for managing correlated attack incidents.
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import logging

from database.incident_models import Incident, IncidentSeverity, IncidentStatus
from database.models import Alert
from correlation.engine import CorrelationEngine

logger = logging.getLogger(__name__)


class IncidentService:
    """Service for incident management and correlation."""

    @staticmethod
    def correlate_recent_alerts(db: Session, hours: int = 24) -> List[Incident]:
        """
        Correlate recent alerts into incidents.

        Args:
            db: Database session
            hours: How many hours back to look

        Returns:
            List of created incidents
        """
        # Get recent alerts
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        alerts = db.query(Alert).filter(
            Alert.timestamp >= cutoff_time
        ).order_by(Alert.timestamp).all()

        if not alerts:
            logger.info("No alerts found for correlation")
            return []

        # Convert to dictionaries
        alert_dicts = [
            {
                'id': alert.id,
                'timestamp': alert.timestamp.isoformat(),
                'threat_class': alert.threat_class,
                'src_ip': alert.src_ip,
                'dst_ip': alert.dst_ip,
                'risk_score': alert.risk_score,
                'severity': alert.severity.value if hasattr(alert.severity, 'value') else str(alert.severity),
                'confidence': alert.confidence
            }
            for alert in alerts
        ]

        # Run correlation
        engine = CorrelationEngine()
        incident_dicts = engine.correlate_alerts(alert_dicts)

        # Create incident objects
        incidents = []
        for incident_dict in incident_dicts:
            incident = IncidentService._create_incident_from_dict(db, incident_dict)
            if incident:
                incidents.append(incident)

        logger.info(f"Correlated {len(alerts)} alerts into {len(incidents)} incidents")
        return incidents

    @staticmethod
    def _create_incident_from_dict(db: Session, incident_dict: Dict[str, Any]) -> Optional[Incident]:
        """
        Create incident database object from dictionary.

        Args:
            db: Database session
            incident_dict: Incident data dictionary

        Returns:
            Created Incident object or None
        """
        try:
            # Check if incident already exists
            existing = db.query(Incident).filter(
                Incident.incident_id == incident_dict['incident_id']
            ).first()

            if existing:
                # Update existing incident
                existing.last_updated = datetime.utcnow()
                existing.risk_score = incident_dict['risk_score']
                existing.severity = IncidentSeverity(incident_dict['severity'])
                existing.alert_count = incident_dict['alert_count']
                existing.related_alert_ids = json.dumps(incident_dict['related_alert_ids'])
                db.commit()
                db.refresh(existing)
                return existing

            # Create new incident
            incident = Incident(
                incident_id=incident_dict['incident_id'],
                start_time=datetime.fromisoformat(incident_dict['start_time'].replace('Z', '+00:00')),
                last_updated=datetime.fromisoformat(incident_dict['last_updated'].replace('Z', '+00:00')),
                duration_minutes=incident_dict.get('duration_minutes', 0),
                risk_score=incident_dict['risk_score'],
                severity=IncidentSeverity(incident_dict['severity']),
                status=IncidentStatus.ACTIVE,
                attack_pattern=incident_dict['attack_pattern'],
                attack_stages_json=json.dumps(incident_dict['attack_stages']),
                summary=incident_dict['summary'],
                affected_assets=json.dumps(incident_dict['affected_assets']),
                source_ips=json.dumps(incident_dict['source_ips']),
                destination_ips=json.dumps(incident_dict['destination_ips']),
                related_alert_ids=json.dumps(incident_dict['related_alert_ids']),
                alert_count=incident_dict['alert_count'],
                correlation_confidence=incident_dict['correlation_confidence'],
                correlation_factors=json.dumps(incident_dict.get('correlation_factors', {}))
            )

            db.add(incident)
            db.commit()
            db.refresh(incident)

            logger.info(f"Created incident: {incident.incident_id}")
            return incident

        except Exception as e:
            logger.error(f"Error creating incident: {e}")
            db.rollback()
            return None

    @staticmethod
    def get_incidents(
        db: Session,
        skip: int = 0,
        limit: int = 50,
        severity: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List[Incident], int]:
        """
        Get incidents with optional filtering.

        Args:
            db: Database session
            skip: Number to skip
            limit: Maximum to return
            severity: Filter by severity
            status: Filter by status

        Returns:
            Tuple of (incidents, total_count)
        """
        query = db.query(Incident)

        if severity:
            query = query.filter(Incident.severity == severity)
        if status:
            query = query.filter(Incident.status == status)

        total = query.count()
        incidents = query.order_by(desc(Incident.start_time)).offset(skip).limit(limit).all()

        return incidents, total

    @staticmethod
    def get_incident_by_id(db: Session, incident_id: str) -> Optional[Incident]:
        """
        Get incident by ID.

        Args:
            db: Database session
            incident_id: Incident ID

        Returns:
            Incident or None
        """
        return db.query(Incident).filter(Incident.incident_id == incident_id).first()

    @staticmethod
    def get_incident_with_alerts(db: Session, incident_id: str) -> Optional[Dict[str, Any]]:
        """
        Get incident with full alert details.

        Args:
            db: Database session
            incident_id: Incident ID

        Returns:
            Dictionary with incident and alert details
        """
        incident = IncidentService.get_incident_by_id(db, incident_id)

        if not incident:
            return None

        # Parse JSON fields
        alert_ids = json.loads(incident.related_alert_ids)
        attack_stages = json.loads(incident.attack_stages_json)
        affected_assets = json.loads(incident.affected_assets)
        correlation_factors = json.loads(incident.correlation_factors) if incident.correlation_factors else {}

        # Get related alerts
        alerts = db.query(Alert).filter(Alert.id.in_(alert_ids)).all()

        # Build timeline
        timeline = []
        for stage in attack_stages:
            alert_id = stage.get('alert_id')
            alert = next((a for a in alerts if a.id == alert_id), None)

            if alert:
                timeline.append({
                    'timestamp': stage['timestamp'],
                    'stage': stage['stage'],
                    'threat_class': stage['threat_class'],
                    'alert_id': alert_id,
                    'src_ip': alert.src_ip,
                    'dst_ip': alert.dst_ip,
                    'risk_score': alert.risk_score,
                    'description': IncidentService._get_stage_description(stage['stage'])
                })

        return {
            'incident_id': incident.incident_id,
            'start_time': incident.start_time.isoformat(),
            'last_updated': incident.last_updated.isoformat(),
            'duration_minutes': incident.duration_minutes,
            'risk_score': incident.risk_score,
            'severity': incident.severity.value if hasattr(incident.severity, 'value') else str(incident.severity),
            'status': incident.status.value if hasattr(incident.status, 'value') else str(incident.status),
            'attack_pattern': incident.attack_pattern,
            'summary': incident.summary,
            'affected_assets': affected_assets,
            'alert_count': incident.alert_count,
            'correlation_confidence': incident.correlation_confidence,
            'correlation_factors': correlation_factors,
            'timeline': timeline,
            'alerts': [
                {
                    'id': alert.id,
                    'timestamp': alert.timestamp.isoformat(),
                    'threat_class': alert.threat_class,
                    'severity': alert.severity.value if hasattr(alert.severity, 'value') else str(alert.severity),
                    'src_ip': alert.src_ip,
                    'dst_ip': alert.dst_ip,
                    'risk_score': alert.risk_score
                }
                for alert in alerts
            ]
        }

    @staticmethod
    def _get_stage_description(stage: str) -> str:
        """Get human-readable stage description."""
        descriptions = {
            'Reconnaissance': 'Reconnaissance activity detected - attacker gathering information',
            'Command and Control': 'Command & Control communications established',
            'Exfiltration': 'Data exfiltration detected - potential data theft',
            'Impact': 'Impact activity detected - system disruption or damage',
            'Discovery': 'Discovery activity - attacker exploring the network'
        }
        return descriptions.get(stage, f"{stage} activity detected")

    @staticmethod
    def get_active_incidents_count(db: Session) -> int:
        """Get count of active incidents."""
        return db.query(Incident).filter(
            Incident.status == IncidentStatus.ACTIVE
        ).count()

    @staticmethod
    def get_critical_incidents_count(db: Session) -> int:
        """Get count of critical incidents."""
        return db.query(Incident).filter(
            and_(
                Incident.severity == IncidentSeverity.CRITICAL,
                Incident.status.in_([IncidentStatus.ACTIVE, IncidentStatus.INVESTIGATING])
            )
        ).count()

    @staticmethod
    def update_incident_status(
        db: Session,
        incident_id: str,
        new_status: str
    ) -> Optional[Incident]:
        """
        Update incident status.

        Args:
            db: Database session
            incident_id: Incident ID
            new_status: New status

        Returns:
            Updated incident or None
        """
        incident = IncidentService.get_incident_by_id(db, incident_id)

        if not incident:
            return None

        try:
            incident.status = IncidentStatus(new_status)
            incident.last_updated = datetime.utcnow()
            db.commit()
            db.refresh(incident)
            return incident
        except Exception as e:
            logger.error(f"Error updating incident status: {e}")
            db.rollback()
            return None
