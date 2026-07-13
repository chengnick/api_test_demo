"""demo loader — 讀 tenants.yaml、模板、mock base url"""
import json
import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def _cfg():
    return yaml.safe_load((ROOT / "config" / "tenants.yaml").read_text(encoding="utf-8")) or {}


def mock_base() -> str:
    return _cfg().get("mock_base", "http://127.0.0.1:8799")


def enabled_tenants(only: str = "") -> list:
    tenants = _cfg().get("tenants", {})
    names = [b for b, c in tenants.items() if (c or {}).get("enabled", True)]
    return [b for b in names if b == only] if only else names


def load_template(mode: str) -> list:
    return json.loads((ROOT / "templates" / f"{mode}_apis.json").read_text(encoding="utf-8"))


def base_url(tenant: str, mode: str) -> str:
    # demo：所有租戶指向本機 mock，用 /{tenant} 路徑區分
    return f"{mock_base()}/{tenant}"


def credentials(tenant: str, mode: str) -> tuple:
    # demo：帳密無關緊要（打 mock），預設值即可，仍支援環境變數覆蓋
    prefix = f"{tenant.upper()}_{mode.upper()}"
    return (os.environ.get(f"{prefix}_LOGIN", "demo_user"),
            os.environ.get(f"{prefix}_PASSWORD", "demo_pass"))
