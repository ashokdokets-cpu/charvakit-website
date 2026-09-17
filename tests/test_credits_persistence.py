"""Local test: prove credits survive process restarts."""
import os
from dotenv import load_dotenv
load_dotenv()

TEST_EMAIL = "persist_test@example.com"


def cleanup():
    from database import db
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM charvak_user_credits WHERE email = %s", (TEST_EMAIL,))
    cur.execute("DELETE FROM charvak_credit_usage_history WHERE email = %s", (TEST_EMAIL,))
    cur.execute("DELETE FROM charvak_credit_purchases WHERE email = %s", (TEST_EMAIL,))
    conn.commit()
    cur.close()
    conn.close()


def run():
    print("=== STEP 0: initialize engine (creates tables) ===")
    from ai_credit_engine import AICreditEngine, CreditPlan
    engine_init = AICreditEngine()  # ensures tables exist
    del engine_init

    print("\n=== STEP 1: clean slate ===")
    cleanup()

    print("\n=== STEP 2: fresh engine instance, initialize user ===")
    from ai_credit_engine import AICreditEngine, CreditPlan
    engine1 = AICreditEngine()
    r = engine1.initialize_user(TEST_EMAIL, CreditPlan.FREE)
    print("init:", r["status"], "credits:", r.get("credits"))
    assert r["status"] == "success"

    print("\n=== STEP 3: deduct some credits ===")
    r = engine1.check_and_deduct(TEST_EMAIL, "chatbot_query")
    print("deduct:", r["status"], "remaining:", r.get("credits_remaining"))
    assert r["status"] == "success"
    assert r["credits_remaining"] == 48

    print("\n=== STEP 4: simulate restart (new engine instance) ===")
    del engine1
    engine2 = AICreditEngine()
    r = engine2.get_user_credits(TEST_EMAIL)
    print("after restart:", r["status"], "remaining:", r.get("credits_remaining"))
    assert r["credits_remaining"] == 48

    print("\n=== STEP 5: purchase a plan ===")
    r = engine2.purchase_credits(TEST_EMAIL, CreditPlan.STARTER, payment_id="test_pay_001")
    print("purchase:", r["status"], "added:", r.get("credits_added"), "total:", r.get("total_credits"))
    assert r["status"] == "success"
    assert r["total_credits"] == 548

    print("\n=== STEP 6: idempotency - same payment_id again ===")
    r = engine2.purchase_credits(TEST_EMAIL, CreditPlan.STARTER, payment_id="test_pay_001")
    print("re-purchase:", r["status"], "already:", r.get("already_credited"))
    assert r.get("already_credited") is True
    assert r["credits_added"] == 0

    print("\n=== STEP 7: usage history persists ===")
    r = engine2.get_user_usage_history(TEST_EMAIL)
    print("history count:", r["count"], "total:", r["total_credits_used"])
    assert r["count"] == 1

    print("\n=== STEP 8: admin stats ===")
    r = engine2.get_admin_stats()
    print("stats:", {k: v for k, v in r["stats"].items() if k != "plans"})

    print("\n=== STEP 9: cleanup ===")
    cleanup()
    print("done")
    print("\nALL TESTS PASSED - credits persist across restarts")


if __name__ == "__main__":
    run()