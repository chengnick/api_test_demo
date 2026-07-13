"""登入測試 —— 每個 tenant × 每個模式各驗一次（登入紅了＝auth 問題，非 API 問題）。"""

def test_login(tenant, mode, sessions):
    sess, base = sessions.get(tenant, mode, required=True)
    assert sess is not None
