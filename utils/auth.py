"""demo auth — 登入 mock 平台取得 token（模擬真實版的 sha1 登入流程）"""
import requests


def login(base_url: str, mode: str, login_name: str, password: str, website: str = "") -> requests.Session:
    s = requests.Session()
    # 真實版這裡是 sha1(sha1(pw)+sessionKey) + POST /auth/{mode}/login；
    # demo 簡化為打 mock 的 /auth/login 取 token。
    r = s.post(f"{base_url}/auth/login",
               data={"login": login_name, "password": password}, timeout=10)
    r.raise_for_status()
    body = r.json()
    if str(body.get("status")) != "200":
        raise RuntimeError(f"login failed: {body.get('message')}")
    s.headers.update({"Authorization": f"Bearer {body['token']}"})
    return s
