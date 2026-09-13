"""
API endpoints for explainable AI threat explanations.
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
import json
from functools import lru_cache

from database.base import get_db
from database.models import Alert
from ml.explainer import get_explainer
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/explanations", tags=["Explanations"])


# Cache explanations for performance (cache 100 most recent)
@lru_cache(maxsize=100)
def _cached_explanation(features_json: str, top_n: int) -> str:
    """
    Cached explanation computation.

    Args:
        features_json: JSON string of features (for hashability)
        top_n: Number of top features

    Returns:
        JSON string of explanation
    """
    features = json.loads(features_json)
    explainer = get_explainer()
    explanation = explainer.explain_prediction(features, top_n=top_n)
    return json.dumps(explanation)


@router.get("/alert/{alert_id}")
async def explain_alert(
    alert_id: int,
    top_n: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get explanation for a specific alert.

    Extracts features from alert evidence and provides
    both technical and human-readable explanations.

    Args:
        alert_id: Alert ID
        top_n: Number of top features to include

    Returns:
        Explanation with technical and human-readable components
    """
    # Get alert
    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    # Extract features from evidence
    try:
        evidence = json.loads(alert.evidence_json) if alert.evidence_json else {}

        # Try to get features from multiple possible locations
        features = evidence.get('features', {})

        if not features:
            # Try key_features from evidence
            features = evidence.get('evidence', {}).get('key_features', {})

        if not features:
            # Try ml_classification evidence
            ml_evidence = evidence.get('evidence', {}).get('ml_classification', {})
            features = ml_evidence.get('features', {})

        if not features or len(features) == 0:
            raise HTTPException(
                status_code=400,
                detail="Alert does not contain extractable features for explanation"
            )

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid evidence JSON in alert"
        )

    # Get cached explanation
    try:
        features_json = json.dumps(features, sort_keys=True)
        explanation_json = _cached_explanation(features_json, top_n)
        explanation = json.loads(explanation_json)

    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate explanation: {str(e)}"
        )

    # Add alert context
    explanation['alert_id'] = alert_id
    explanation['alert_threat_class'] = alert.threat_class
    explanation['alert_confidence'] = alert.confidence
    explanation['alert_risk_score'] = alert.risk_score

    return explanation


@router.post("/explain")
async def explain_features(
    features: Dict[str, float],
    top_n: int = 10
):
    """
    Get explanation for arbitrary feature set.

    Useful for explaining predictions without storing as alerts.

    Args:
        features: Dictionary of feature values
        top_n: Number of top features to include

    Returns:
        Explanation dictionary
    """
    try:
        # Use cached explanation
        features_json = json.dumps(features, sort_keys=True)
        explanation_json = _cached_explanation(features_json, top_n)
        explanation = json.loads(explanation_json)

        return explanation

    except Exception as e:
        logger.error(f"Error generating explanation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate explanation: {str(e)}"
        )


@router.get("/cache/stats")
async def get_cache_stats():
    """
    Get explanation cache statistics.

    Returns:
        Cache hit/miss statistics
    """
    cache_info = _cached_explanation.cache_info()

    return {
        "cache_size": cache_info.currsize,
        "max_size": cache_info.maxsize,
        "hits": cache_info.hits,
        "misses": cache_info.misses,
        "hit_rate": (
            cache_info.hits / (cache_info.hits + cache_info.misses)
            if (cache_info.hits + cache_info.misses) > 0
            else 0.0
        )
    }


@router.post("/cache/clear")
async def clear_cache():
    """
    Clear explanation cache.

    Useful after model retraining or for troubleshooting.
    """
    _cached_explanation.cache_clear()

    return {
        "status": "success",
        "message": "Explanation cache cleared"
    }
