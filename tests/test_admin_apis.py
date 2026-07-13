"""後台 admin API 測試 —— 對每個 tenant × 每支後台 API 自動展開。"""
MODE = "admin"
from utils.api import call_api, assert_api_ok


def test_admin_api(tenant, api, sessions):
    sess, base = sessions.get(tenant, "admin")
    resp = call_api(sess, base, api)
    assert_api_ok(resp, f"{tenant}/{api['name']}", expect=api.get("expect"))
