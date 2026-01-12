"""
healthcheckx
============

Production-grade health checks for Python applications.
Simple, extensible, and framework-friendly.
"""

# -----------------------------
# Core API
# -----------------------------
from .core import Health, overall_status

# -----------------------------
# Result models
# -----------------------------
from .result import CheckResult, HealthStatus

# -----------------------------
# Framework adapters (optional but convenient)
# -----------------------------
try:
    from .adapters.fastapi import FastAPIAdapter
except Exception:  # FastAPI not installed
    FastAPIAdapter = None

try:
    from .adapters.flask import flask_health_endpoint
except Exception:  # Flask not installed
    flask_health_endpoint = None

try:
    from .adapters.django import django_health_view
except Exception:  # Django not installed
    django_health_view = None

# -----------------------------
# Public API
# -----------------------------
__all__ = [
    "Health",
    "overall_status",
    "CheckResult",
    "HealthStatus",
    "FastAPIAdapter",
    "flask_health_endpoint",
    "django_health_view",
]
