"""
mock_platform/server.py — 內建測試用平台（純標準庫，無外部依賴）

模擬一個需要登入的 API 平台，讓 demo 不依賴任何真實或外部服務：
- POST /auth/login          → 回傳 token（模擬 sha1 加密登入的結果）
- 其餘 /api/... 端點         → 需帶 token，回傳 {"status": "200", ...}

多個「租戶」在 demo 裡都指向同一個 mock（用路徑前綴 /{tenant} 區分，
內容相同）——重點是展示框架如何「對 N 個租戶套用同一批測試」。
"""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DEMO_PORT = 8799
VALID_TOKEN = "demo-token-abc123"

# 已知端點（去掉 /{tenant} 前綴後比對）；未知端點回 404 status
KNOWN_PATHS = {
    "/auth/login",
    "/api/admin/profile",
    "/api/admin/accounts",
    "/api/admin/report/summary",
    "/api/admin/transactions",
    "/api/user/balance",
    "/api/user/banking/history",
    "/api/user/inbox",
    "/api/user/promotions",
}


def _strip_tenant(path: str) -> str:
    # /{tenant}/api/... → /api/...   ；/{tenant}/auth/login → /auth/login
    parts = path.split("?", 1)[0].split("/")
    # parts = ['', tenant, 'api', ...] → 去掉租戶段
    if len(parts) >= 3 and parts[1] not in ("api", "auth"):
        return "/" + "/".join(parts[2:])
    return path.split("?", 1)[0]


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # 靜音

    def _json(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._route("GET")

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        self._body = self.rfile.read(length) if length else b""
        self._route("POST")

    def _route(self, method):
        path = _strip_tenant(self.path)

        if path == "/auth/login":
            return self._json(200, {"status": "200", "token": VALID_TOKEN, "message": "ok"})

        if path not in KNOWN_PATHS:
            return self._json(200, {"status": "404", "message": f"{path} is not supported"})

        # 受保護端點：檢查 token
        auth = self.headers.get("Authorization", "")
        if VALID_TOKEN not in auth:
            return self._json(200, {"status": "401", "message": "unauthorized"})

        return self._json(200, {"status": "200", "data": [], "path": path, "method": method})


def start_mock_server(port: int = DEMO_PORT):
    """在背景執行緒啟動 mock server，回傳 server 物件（呼叫 .shutdown() 關閉）。"""
    server = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server


if __name__ == "__main__":
    s = start_mock_server()
    print(f"Mock platform running on http://127.0.0.1:{DEMO_PORT} (Ctrl+C to stop)")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        s.shutdown()
