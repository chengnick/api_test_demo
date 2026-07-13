"""前台 user API 測試 —— 對每個 tenant × 每支前台 API 自動展開。"""
MODE = "user"
from utils.api import call_api, assert_api_ok


def test_user_api(tenant, api, sessions):
    sess, base = sessions.get(tenant, "user")
    resp = call_api(sess, base, api)
    assert_api_ok(resp, f"{tenant}/{api['name']}", expect=api.get("expect"))
