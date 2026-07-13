"""
conftest.py — demo 框架核心

- 自動啟動內建 mock 平台（session 開始時），結束時關閉 → 零外部依賴
- pytest_generate_tests：
    * (tenant, api)  → tenant × API 展開；預設只跑 readonly（--include-writes 才含寫入型）
    * (tenant, mode) → 登入測試，tenant × mode
- session 快取：每個 (tenant, mode) 只登入一次
"""

import pytest

from mock_platform.server import start_mock_server, DEMO_PORT
from utils import loader, auth

MODES = ("admin", "user")


@pytest.fixture(scope="session", autouse=True)
def mock_server():
    server = start_mock_server(DEMO_PORT)
    yield server
    server.shutdown()


def pytest_addoption(parser):
    parser.addoption("--tenant", action="store", default="", help="只跑指定 tenant")
    parser.addoption("--include-writes", action="store_true", default=False,
                     help="連寫入型端點也測（預設只測 readonly）")


def pytest_generate_tests(metafunc):
    fx = set(metafunc.fixturenames)
    only = metafunc.config.getoption("--tenant")
    tenants = loader.enabled_tenants(only)

    if {"tenant", "mode"} <= fx and "api" not in fx:
        params = [(b, m) for b in tenants for m in MODES]
        metafunc.parametrize("tenant,mode", params, ids=[f"{b}-{m}" for b, m in params])
        return

    if {"tenant", "api"} <= fx:
        mode = getattr(metafunc.module, "MODE", None)
        if mode not in MODES:
            return
        apis = loader.load_template(mode)
        if not metafunc.config.getoption("--include-writes"):
            apis = [a for a in apis if a.get("readonly", True)]
        params = [(b, a) for b in tenants for a in apis]
        ids = [f"{b}-{a['method']}-{a['name']}" for b, a in params]
        metafunc.parametrize("tenant,api", params, ids=ids)


class SessionCache:
    def __init__(self):
        self._cache = {}

    def get(self, tenant, mode, required=False):
        key = (tenant, mode)
        if key not in self._cache:
            base = loader.base_url(tenant, mode)
            login_name, password = loader.credentials(tenant, mode)
            self._cache[key] = (auth.login(base, mode, login_name, password), base)
        return self._cache[key]


@pytest.fixture(scope="session")
def sessions():
    return SessionCache()
