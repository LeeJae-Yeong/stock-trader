"""추천 모듈"""
from .strategy import (
    Recommendation,
    add_technical_indicators,
    evaluate_rising_star,
    evaluate_stock,
)

__all__ = [
    "Recommendation",
    "evaluate_stock",
    "evaluate_rising_star",
    "add_technical_indicators",
]
