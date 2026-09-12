import shutil, datetime

ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
path = "main.py"
shutil.copy(path, f"{path}.bak-{ts}")

with open(path, "r", encoding="utf-8") as f:
    c = f.read()

old_block = '''        # Check verification
        from email_verification import email_verification
        if not email_verification.is_verified(data.email):
            # Allow admin without verification
            if data.email != "charvakit@gmail.com":
                pass  # Temporarily allow all - enable below line after transition
                # return JSONResponse({"status": "error", "message": "Please verify your email first. Check your inbox."}, status_code=403)'''

new_block = '''        # Check email verification (admins bypass)
        ADMIN_EMAILS_SET = {"charvakit@gmail.com", "hr@charvakit.com"}
        from email_verification import email_verification
        if data.email not in ADMIN_EMAILS_SET:
            if not email_verification.is_verified(data.email):
                return JSONResponse({
                    "status": "error",
                    "message": "Please verify your email before logging in. Check your inbox for the verification link.",
                    "action": "verify_email"
                }, status_code=403)'''

if old_block in c:
    c = c.replace(old_block, new_block, 1)
    print("[OK] main.py: email verification ENABLED (admins bypass)")
else:
    print("[ERROR] Block not found. Current lines 1043-1055:")
    lines = c.split("\n")
    for i in range(1042, min(1056, len(lines))):
        print(f"  {i+1}: {lines[i]}")
    raise SystemExit(1)

with open(path, "w", encoding="utf-8", newline="") as f:
    f.write(c)

# Verify
import ast
try:
    ast.parse(open(path, "r", encoding="utf-8").read())
    print("[OK] main.py parses cleanly")
except SyntaxError as e:
    print(f"[ERROR] Syntax error: {e}")
    raise SystemExit(1)
