"""
api.py — 依模板呼叫 API、組參數、分層斷言（含失敗時的 request/response dump）

- 智慧參數：日期/分頁類參數自動帶合理預設（今天、30 天前、1、10）；
  模板可用 "param_values" 覆蓋成真實範例值。
- 分層斷言：預設寬鬆（HTTP 200 + 業務 status）；模板可加 "expect": {"fields": [...]}
  對核心 API 檢查關鍵欄位是否存在。
- 失敗 dump：任何斷言失敗都會附上「送了什麼、回了什麼」，方便直接除錯。
"""

from __future__ import annotations

import datetime
from typing import Any

import requests

_TODAY = datetime.date.today()
_MONTH_AGO = _TODAY - datetime.timedelta(days=30)

# 業務失敗的 status 碼（依平台調整）
ERROR_STATUS = {"401", "403", "404", "500", "999"}


def _smart_default(key: str) -> str:
    """依參數名稱猜一個合理預設值，讓請求更接近真實、減少因缺參數的假失敗。"""
    k = key.lower()
    if any(t in k for t in ("starttime", "startdate")) or k == "start":
        return _MONTH_AGO.isoformat()
    if any(t in k for t in ("endtime", "enddate")) or k == "end":
        return _TODAY.isoformat()
    if "size" in k or "limit" in k or "length" in k:
        return "10"
    if "page" in k:
        return "1"
    return ""


def build_params(api: dict) -> dict:
    """組請求參數：優先用模板的 param_values，其次智慧預設。"""
    overrides = api.get("param_values", {}) or {}
    return {k: overrides.get(k, _smart_default(k)) for k in api.get("params", [])}


def call_api(session: requests.Session, base_url: str, api: dict) -> requests.Response:
    """依模板送出請求；把送出的內容掛在 response 上供失敗 dump 用。"""
    url = base_url + api["path"]
    data = build_params(api)
    if api["method"] == "GET":
        resp = session.get(url, params=data, timeout=20)
    else:
        resp = session.post(url, data=data, timeout=20)
    resp._sent = {"method": api["method"], "url": url, "params": data}  # type: ignore[attr-defined]
    return resp


def _dump(resp: requests.Response) -> str:
    """失敗時的診斷資訊：送出的 request + 回傳的 response（截斷）。"""
    sent = getattr(resp, "_sent", {})
    try:
        body = resp.text[:400]
    except Exception:
        body = "<無法讀取 body>"
    return (f"\n    → {sent.get('method')} {sent.get('url')}"
            f"\n    → params: {sent.get('params')}"
            f"\n    ← HTTP {resp.status_code}: {body}")


def _has_field(body: Any, dotted: str) -> bool:
    """支援 'a.b.c' 巢狀欄位檢查。"""
    cur = body
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return False
    return True


def assert_api_ok(resp: requests.Response, name: str, expect: dict | None = None) -> None:
    """分層斷言：HTTP 200 → 業務 status → （選配）關鍵欄位存在。失敗都附 dump。"""
    assert resp.status_code == 200, f"{name} HTTP {resp.status_code}{_dump(resp)}"

    try:
        body = resp.json()
    except Exception:
        return  # 非 JSON → 只驗 HTTP

    if isinstance(body, dict):
        status = str(body.get("status", ""))
        if status:
            msg = body.get("message") or body.get("msg") or ""
            assert status not in ERROR_STATUS, \
                f"{name} 業務失敗 status={status} {msg}{_dump(resp)}"

    # 分層斷言（選配）：模板有 expect.fields 才檢查關鍵欄位
    if expect:
        for field in expect.get("fields", []):
            assert _has_field(body, field), \
                f"{name} 缺關鍵欄位 '{field}'{_dump(resp)}"
