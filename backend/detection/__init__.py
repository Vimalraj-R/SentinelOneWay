"""
ML-based threat detection module for SentinelOneWay.

Provides trained model loading and prediction capabilities.
"""
from .classifier import MLThreatClassifier

__all__ = ['MLThreatClassifier']
