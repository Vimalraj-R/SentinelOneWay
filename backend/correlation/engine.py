"""
Attack correlation engine for SentinelOneWay.

Correlates low-level alerts into higher-level incidents using:
- Temporal proximity
- IP address relationships
- Asset involvement
- Threat class sequences
- Communication patterns

Rule-based implementation - no LLMs.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List, Dict, Any, Set, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json
import logging

logger = logging.getLogger(__name__)


class CorrelationEngine:
    """
    Rule-based attack correlation engine.

    Identifies multi-stage attacks by correlating related alerts
    based on temporal, network, and behavioral patterns.
    """

    # Correlation configuration
    MAX_TIME_GAP_MINUTES = 60  # Max time between related alerts
    MIN_ALERTS_FOR_INCIDENT = 2  # Minimum alerts to form incident
    MIN_CORRELATION_SCORE = 0.6  # Minimum correlation confidence

    # Attack stage mappings
    THREAT_TO_STAGE = {
        'PORT_SCAN': 'Reconnaissance',
        'SYN_FLOOD': 'Impact',
        'C2_BEACON': 'Command and Control',
        'DNS_TUNNEL': 'Command and Control',
        'DATA_EXFILTRATION': 'Exfiltration',
        'SUSPICIOUS': 'Discovery',
        'UNKNOWN_ANOMALY': 'Discovery'
    }

    # Attack pattern templates
    ATTACK_PATTERNS = [
        {
            'name': 'Multi-stage Compromise',
            'stages': ['Reconnaissance', 'Command and Control', 'Exfiltration'],
            'description': 'Full attack chain from initial recon to data theft'
        },
        {
            'name': 'Reconnaissance to C2',
            'stages': ['Reconnaissance', 'Command and Control'],
            'description': 'Scanning followed by command and control establishment'
        },
        {
            'name': 'C2 with Exfiltration',
            'stages': ['Command and Control', 'Exfiltration'],
            'description': 'Active C2 channel with data exfiltration'
        },
        {
            'name': 'DDoS Campaign',
            'stages': ['Reconnaissance', 'Impact'],
            'description': 'Scanning followed by volumetric attack'
        },
        {
            'name': 'Persistent C2 Activity',
            'stages': ['Command and Control'],
            'description': 'Sustained command and control communications'
        }
    ]

    def __init__(self):
        """Initialize correlation engine."""
        pass

    def correlate_alerts(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Correlate alerts into incidents.

        Args:
            alerts: List of alert dictionaries

        Returns:
            List of incident dictionaries
        """
        if len(alerts) < self.MIN_ALERTS_FOR_INCIDENT:
            return []

        # Sort alerts by timestamp
        sorted_alerts = sorted(alerts, key=lambda a: a.get('timestamp', ''))

        # Build correlation groups
        correlation_groups = self._build_correlation_groups(sorted_alerts)

        # Create incidents from groups
        incidents = []
        for group in correlation_groups:
            if len(group) >= self.MIN_ALERTS_FOR_INCIDENT:
                incident = self._create_incident_from_group(group)
                if incident:
                    incidents.append(incident)

        return incidents

    def _build_correlation_groups(self, alerts: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """
        Build correlation groups using sliding time window.

        Args:
            alerts: Sorted list of alerts

        Returns:
            List of alert groups
        """
        groups = []
        current_group = []

        for alert in alerts:
            if not current_group:
                # Start new group
                current_group.append(alert)
            else:
                # Check if alert correlates with current group
                if self._should_correlate(alert, current_group):
                    current_group.append(alert)
                else:
                    # Save current group and start new one
                    if len(current_group) >= self.MIN_ALERTS_FOR_INCIDENT:
                        groups.append(current_group)
                    current_group = [alert]

        # Add final group
        if len(current_group) >= self.MIN_ALERTS_FOR_INCIDENT:
            groups.append(current_group)

        return groups

    def _should_correlate(self, alert: Dict[str, Any], group: List[Dict[str, Any]]) -> bool:
        """
        Determine if alert should be correlated with existing group.

        Args:
            alert: Alert to check
            group: Existing alert group

        Returns:
            True if alert should be added to group
        """
        # Get correlation factors
        factors = self._calculate_correlation_factors(alert, group)

        # Calculate weighted correlation score
        correlation_score = self._calculate_correlation_score(factors)

        return correlation_score >= self.MIN_CORRELATION_SCORE

    def _calculate_correlation_factors(self,
                                      alert: Dict[str, Any],
                                      group: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate correlation factors between alert and group.

        Args:
            alert: Alert to check
            group: Alert group

        Returns:
            Dictionary of correlation factors
        """
        factors = {}

        # Temporal proximity (most recent alert in group)
        last_alert = group[-1]
        factors['temporal'] = self._temporal_proximity(alert, last_alert)

        # Source IP overlap
        factors['source_ip'] = self._ip_overlap(
            alert.get('src_ip'),
            [a.get('src_ip') for a in group]
        )

        # Destination IP overlap
        factors['destination_ip'] = self._ip_overlap(
            alert.get('dst_ip'),
            [a.get('dst_ip') for a in group]
        )

        # Asset involvement (either source or destination)
        alert_assets = {alert.get('src_ip'), alert.get('dst_ip')}
        group_assets = set()
        for a in group:
            group_assets.add(a.get('src_ip'))
            group_assets.add(a.get('dst_ip'))

        factors['asset_overlap'] = len(alert_assets & group_assets) / max(len(alert_assets | group_assets), 1)

        # Threat progression (logical attack sequence)
        factors['threat_progression'] = self._threat_progression_score(alert, group)

        # Risk score similarity
        alert_risk = alert.get('risk_score', 0)
        group_risks = [a.get('risk_score', 0) for a in group]
        avg_group_risk = sum(group_risks) / len(group_risks) if group_risks else 0
        risk_diff = abs(alert_risk - avg_group_risk)
        factors['risk_similarity'] = 1.0 - min(risk_diff / 100.0, 1.0)

        return factors

    def _temporal_proximity(self, alert1: Dict[str, Any], alert2: Dict[str, Any]) -> float:
        """
        Calculate temporal proximity score.

        Args:
            alert1: First alert
            alert2: Second alert

        Returns:
            Proximity score (0.0-1.0)
        """
        try:
            time1 = datetime.fromisoformat(alert1['timestamp'].replace('Z', '+00:00'))
            time2 = datetime.fromisoformat(alert2['timestamp'].replace('Z', '+00:00'))

            time_diff = abs((time1 - time2).total_seconds() / 60)  # Minutes

            if time_diff > self.MAX_TIME_GAP_MINUTES:
                return 0.0

            # Linear decay: 1.0 at 0 minutes, 0.0 at MAX_TIME_GAP
            return 1.0 - (time_diff / self.MAX_TIME_GAP_MINUTES)

        except Exception as e:
            logger.warning(f"Error calculating temporal proximity: {e}")
            return 0.0

    def _ip_overlap(self, ip: str, ip_list: List[str]) -> float:
        """
        Calculate IP overlap score.

        Args:
            ip: IP address to check
            ip_list: List of IPs to compare against

        Returns:
            Overlap score (0.0-1.0)
        """
        if not ip or not ip_list:
            return 0.0

        # Exact match
        if ip in ip_list:
            return 1.0

        # Subnet proximity (basic /24 check)
        ip_subnet = '.'.join(ip.split('.')[:3])
        for other_ip in ip_list:
            if other_ip:
                other_subnet = '.'.join(other_ip.split('.')[:3])
                if ip_subnet == other_subnet:
                    return 0.7  # Same subnet

        return 0.0

    def _threat_progression_score(self, alert: Dict[str, Any], group: List[Dict[str, Any]]) -> float:
        """
        Calculate threat progression score (logical attack sequence).

        Args:
            alert: Alert to check
            group: Alert group

        Returns:
            Progression score (0.0-1.0)
        """
        alert_threat = alert.get('threat_class', '')
        group_threats = [a.get('threat_class', '') for a in group]

        # Map threats to stages
        alert_stage = self.THREAT_TO_STAGE.get(alert_threat)
        group_stages = [self.THREAT_TO_STAGE.get(t) for t in group_threats if self.THREAT_TO_STAGE.get(t)]

        if not alert_stage or not group_stages:
            return 0.5  # Neutral if can't determine

        # Check for logical progression
        logical_sequences = [
            ['Reconnaissance', 'Discovery'],
            ['Reconnaissance', 'Command and Control'],
            ['Discovery', 'Command and Control'],
            ['Command and Control', 'Exfiltration'],
            ['Reconnaissance', 'Impact']
        ]

        # Check if adding this alert creates logical sequence
        for prev_stage in group_stages:
            if [prev_stage, alert_stage] in logical_sequences:
                return 1.0  # Perfect progression

        # Same stage (repeated activity)
        if alert_stage in group_stages:
            return 0.8

        return 0.3  # No clear progression

    def _calculate_correlation_score(self, factors: Dict[str, float]) -> float:
        """
        Calculate weighted correlation score.

        Args:
            factors: Correlation factors

        Returns:
            Weighted score (0.0-1.0)
        """
        # Weights for different factors
        weights = {
            'temporal': 0.30,
            'asset_overlap': 0.25,
            'threat_progression': 0.20,
            'source_ip': 0.10,
            'destination_ip': 0.10,
            'risk_similarity': 0.05
        }

        score = sum(factors.get(factor, 0.0) * weight for factor, weight in weights.items())
        return score

    def _create_incident_from_group(self, group: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Create incident from correlated alert group.

        Args:
            group: List of correlated alerts

        Returns:
            Incident dictionary or None
        """
        if not group:
            return None

        # Sort by timestamp
        group = sorted(group, key=lambda a: a.get('timestamp', ''))

        # Extract attack stages
        attack_stages = []
        seen_stages = set()
        for alert in group:
            threat_class = alert.get('threat_class', '')
            stage = self.THREAT_TO_STAGE.get(threat_class)
            if stage and stage not in seen_stages:
                attack_stages.append({
                    'stage': stage,
                    'threat_class': threat_class,
                    'timestamp': alert.get('timestamp'),
                    'alert_id': alert.get('id')
                })
                seen_stages.add(stage)

        # Identify attack pattern
        stage_names = [s['stage'] for s in attack_stages]
        attack_pattern = self._identify_attack_pattern(stage_names)

        # Extract affected entities
        source_ips = list(set(a.get('src_ip') for a in group if a.get('src_ip')))
        destination_ips = list(set(a.get('dst_ip') for a in group if a.get('dst_ip')))
        affected_assets = list(set(source_ips + destination_ips))

        # Calculate incident risk score
        risk_scores = [a.get('risk_score', 0) for a in group]
        max_risk = max(risk_scores) if risk_scores else 0
        avg_risk = sum(risk_scores) / len(risk_scores) if risk_scores else 0

        # Boost risk for multi-stage attacks
        stage_count = len(attack_stages)
        risk_multiplier = 1.0 + (stage_count - 1) * 0.1  # +10% per additional stage
        incident_risk = min(int(max_risk * risk_multiplier), 100)

        # Determine severity
        if incident_risk >= 85:
            severity = 'Critical'
        elif incident_risk >= 70:
            severity = 'High'
        elif incident_risk >= 50:
            severity = 'Medium'
        else:
            severity = 'Low'

        # Calculate correlation confidence
        correlation_confidence = self._calculate_group_correlation_confidence(group)

        # Generate summary
        summary = self._generate_incident_summary(attack_pattern, attack_stages, affected_assets, incident_risk)

        # Calculate duration
        start_time = datetime.fromisoformat(group[0]['timestamp'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(group[-1]['timestamp'].replace('Z', '+00:00'))
        duration_minutes = (end_time - start_time).total_seconds() / 60

        return {
            'incident_id': f"INC-{start_time.strftime('%Y%m%d')}-{hash(tuple(a.get('id') for a in group)) % 10000:04d}",
            'start_time': group[0]['timestamp'],
            'last_updated': group[-1]['timestamp'],
            'duration_minutes': duration_minutes,
            'risk_score': incident_risk,
            'severity': severity,
            'status': 'Active',
            'attack_pattern': attack_pattern,
            'attack_stages': attack_stages,
            'summary': summary,
            'affected_assets': affected_assets,
            'source_ips': source_ips,
            'destination_ips': destination_ips,
            'related_alert_ids': [a.get('id') for a in group],
            'alert_count': len(group),
            'correlation_confidence': correlation_confidence,
            'correlation_factors': {
                'temporal_span_minutes': duration_minutes,
                'unique_stages': len(attack_stages),
                'unique_assets': len(affected_assets),
                'alert_density': len(group) / max(duration_minutes, 1)
            }
        }

    def _identify_attack_pattern(self, stages: List[str]) -> str:
        """
        Identify attack pattern from stages.

        Args:
            stages: List of attack stages

        Returns:
            Attack pattern name
        """
        stages_set = set(stages)

        # Check known patterns
        for pattern in self.ATTACK_PATTERNS:
            pattern_stages = set(pattern['stages'])
            if pattern_stages.issubset(stages_set):
                return pattern['name']

        # Default based on stage count
        if len(stages) >= 3:
            return 'Multi-stage Compromise'
        elif len(stages) == 2:
            return 'Two-stage Attack'
        else:
            return 'Coordinated Activity'

    def _calculate_group_correlation_confidence(self, group: List[Dict[str, Any]]) -> float:
        """
        Calculate overall correlation confidence for group.

        Args:
            group: Alert group

        Returns:
            Confidence score (0.0-1.0)
        """
        if len(group) < 2:
            return 1.0

        # Calculate average pairwise correlation
        total_score = 0.0
        count = 0

        for i in range(len(group) - 1):
            factors = self._calculate_correlation_factors(group[i + 1], group[:i + 1])
            score = self._calculate_correlation_score(factors)
            total_score += score
            count += 1

        return total_score / count if count > 0 else 0.0

    def _generate_incident_summary(self,
                                  pattern: str,
                                  stages: List[Dict[str, Any]],
                                  assets: List[str],
                                  risk: int) -> str:
        """
        Generate human-readable incident summary.

        Args:
            pattern: Attack pattern name
            stages: Attack stages
            assets: Affected assets
            risk: Risk score

        Returns:
            Summary string
        """
        stage_descriptions = []
        for stage_info in stages:
            stage = stage_info['stage']
            threat = stage_info['threat_class']

            if stage == 'Reconnaissance':
                stage_descriptions.append('reconnaissance observed')
            elif stage == 'Command and Control':
                stage_descriptions.append('command-and-control traffic detected')
            elif stage == 'Exfiltration':
                stage_descriptions.append('data exfiltration observed')
            elif stage == 'Impact':
                stage_descriptions.append('impact activity detected')
            elif stage == 'Discovery':
                stage_descriptions.append('discovery activity observed')

        summary_parts = []
        summary_parts.append(f"Detected {pattern.lower()} affecting {len(assets)} asset(s).")

        if stage_descriptions:
            summary_parts.append(f"Attack sequence: {' -> '.join(stage_descriptions)}.")

        if risk >= 85:
            summary_parts.append("CRITICAL THREAT requiring immediate response.")
        elif risk >= 70:
            summary_parts.append("High-risk threat requiring urgent investigation.")

        return ' '.join(summary_parts)
