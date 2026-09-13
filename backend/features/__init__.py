"""
Feature engineering module for SentinelOneWay.

Converts raw network flow records into numerical features
suitable for machine learning models.
"""
from .extractor import FlowFeatureExtractor

__all__ = ['FlowFeatureExtractor']
