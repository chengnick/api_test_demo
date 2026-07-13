"""T3 verification only — intentional failures to exercise analyze-offline.
Delete this file after T3 sign-off. Do NOT merge to main.
"""
import pytest
import requests


def test_t3_ambiguous_failure():
    """模糊型:單純斷言錯,rules 攔不到,應走 --no-ai 佔位分類。"""
    result = {"status": "ok", "count": 3}
    assert result["count"] == 999, "intentional mismatch for T3 verification"


def test_t3_environment_failure():
    """環境型:connection error,應被 rule-based 預分類命中。"""
    requests.get("http://localhost:59999/nonexistent", timeout=2)
