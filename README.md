# Multi-Tenant API Test Framework — Demo

<!-- 把 USER/REPO 換成你的 GitHub 帳號與 repo 名，badge 就會顯示 CI 狀態 -->
![CI](https://github.com/chengnick/api_test_demo/actions/workflows/ci.yml/badge.svg)

> A data-driven API regression framework that runs the **same test suite across N tenants** —
> adding a new tenant takes **one line of config**, not a rewrite.
>
> This is a **self-contained, sanitized demo**: it ships with a built-in mock platform, so
> `pip install && pytest` runs green with **zero external setup**. No real service required.

繁中：這是一套「一份 API 模板、自動套用到 N 個租戶」的資料驅動測試框架 demo。
內建 mock 平台，`pytest` 直接全綠，不需要任何真實服務或帳號。

---

## Quick start

```bash
pip install -r requirements.txt
pytest
```

That's it. A built-in mock platform starts automatically, and the suite runs green:

```
tests/test_admin_apis.py .............  [ 40%]
tests/test_login.py      ......         [ 60%]
tests/test_user_apis.py  .............  [100%]
30 passed
```

30 tests = **3 tenants × (4 admin + 4 user APIs + 2 login modes)**. Run a single tenant:

```bash
pytest --tenant alpha
```

---

## The idea

The framework separates **discovery** from **testing**:

```
  Scanner (run once)                 This framework (run always)
  ──────────────────                 ───────────────────────────
  Auto-discovers a platform's        Reads tenants.yaml + templates,
  APIs → produces JSON templates     runs them across every tenant
        │                                     ▲
        └─────────── templates ───────────────┘
   Done occasionally, by a maintainer    Adding a tenant = one line
```

Because every tenant runs the **same system / same APIs** (only the domain differs), you
don't re-scan per tenant. Scan once to build tenant-agnostic templates; the framework
parametrizes **tenant × API** and applies them to all tenants.

*(In this demo, all tenants point at the bundled mock platform to keep it self-contained.
In the real system, each tenant's base URL is derived from its name.)*

---

## Layout

```
api_test_demo/
├── mock_platform/server.py   # built-in fake platform (stdlib only) — login + APIs
├── config/tenants.yaml        # tenant list — add a tenant here
├── templates/
│   ├── admin_apis.json       # tenant-agnostic endpoint templates
│   └── user_apis.json
├── conftest.py               # starts mock, parametrizes tenant×API, caches login
├── tests/
│   ├── test_admin_apis.py
│   └── test_user_apis.py
└── utils/                    # auth / api-call / loader
```

## Add a tenant

```yaml
# config/tenants.yaml
tenants:
  delta:
    enabled: true
```

Run `pytest --tenant delta`. No test code changes. That's the whole point.

---

## Key design points

- **Data-driven parametrization** — `pytest_generate_tests` expands every `tenant × API`
  into an individual test, with readable IDs (`alpha-POST-summary`).
- **Login as a separate test** — `tests/test_login.py` verifies auth per tenant×mode.
  A red login test means *auth* is broken (creds/env), not an API — easy to tell apart.
- **Read-only by default** — every template carries a `readonly` flag; the suite only runs
  read-only endpoints unless `--include-writes` is passed, so it never pollutes an environment.
- **Login once per (tenant, mode)** — session cached and reused across all that tenant's APIs.
- **Env-var credentials** — real deployments read creds from environment / `.env`
  (`{TENANT}_{MODE}_LOGIN` / `_PASSWORD`); the demo uses harmless defaults against the mock.
- **Self-contained** — the mock platform (`mock_platform/server.py`) uses only the Python
  standard library, so the demo has no external moving parts and always reproduces.

---

## Notes

This demo is a **sanitized** illustration of a system originally built to automate API
regression for a multi-tenant platform. It reproduces the architecture and testing approach
without any real endpoints, domains, or credentials.

The engineering story behind it — auto-discovering interaction-triggered APIs, making the
scan deterministic, handling driver instability, and the scan-once/apply-to-N architecture —
is written up separately.

---

## CI & reports

- **GitHub Actions** (`.github/workflows/ci.yml`) runs the suite on every push across
  Python 3.9 / 3.11 / 3.12 — green with no secrets, because the demo is self-contained.
- **Allure**: results are produced with `--alluredir` and uploaded as a CI artifact.
  Locally:

  ```bash
  pip install allure-pytest
  pytest --alluredir=allure-results
  allure serve allure-results
  <!-- Create report -->
  allure generate allure-results -o allure-report 
  ```

  Failed assertions carry the full request/response dump, so the Allure report shows
  exactly what was sent and returned.