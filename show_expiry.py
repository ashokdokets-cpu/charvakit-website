with open('password_reset.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== EXPIRY LINES IN password_reset.py ===")
for i, line in enumerate(lines):
    if 'timedelta' in line or 'expires_at' in line:
        print(f"Line {i+1}: {line.strip()}")
