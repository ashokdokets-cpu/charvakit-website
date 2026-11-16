#!/usr/bin/env python3
"""
Charvak Secret Scanner - Pre-commit hook.
Scans staged files for hardcoded secrets before allowing commit.
"""
import re
import subprocess
import sys
from pathlib import Path

# Patterns that indicate leaked secrets
PATTERNS = [
    # PostgreSQL connection strings with password
    (r'postgresql://[^:\s]+:[^@\s]{8,}@', "PostgreSQL connection with hardcoded password"),
    (r'postgres://[^:\s]+:[^@\s]{8,}@', "PostgreSQL connection (short form) with password"),
    
    # MongoDB
    (r'mongodb(\+srv)?://[^:\s]+:[^@\s]+@', "MongoDB connection with password"),
    
    # API keys by provider
    (r'sk-[a-zA-Z0-9_-]{20,}', "OpenAI/Stripe-style key (sk-...)"),
    (r'xkeysib-[a-zA-Z0-9]{40,}', "Brevo API key"),
    (r'SG\.[a-zA-Z0-9_-]{22,}', "SendGrid API key"),
    (r'AIza[a-zA-Z0-9_-]{35}', "Google API key"),
    (r'AKIA[A-Z0-9]{16}', "AWS Access Key ID"),
    (r'sk_live_[a-zA-Z0-9]{20,}', "Stripe live key"),
    (r'sk_test_[a-zA-Z0-9]{20,}', "Stripe test key"),
    
    # Generic tokens
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub personal access token"),
    (r'ghs_[a-zA-Z0-9]{36}', "GitHub server token"),
    (r'xox[baprs]-[a-zA-Z0-9-]{10,}', "Slack token"),
    
    # Private keys
    (r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----', "Private key block"),
]

# Files to skip (test fixtures, docs, etc.)
SKIP_EXTENSIONS = {'.md', '.txt', '.rst', '.example', '.sample', '.template'}
SKIP_PATHS = {'node_modules/', 'venv/', '.venv/', '__pycache__/', '.git/'}
SKIP_FILES = {'.env', '.env.local', '.env.example', '.env.sample'}

# File size limit (don't scan giant binary files)
MAX_SCAN_SIZE = 5 * 1024 * 1024  # 5 MB


def get_staged_files():
    """Get list of files being committed."""
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
        capture_output=True, text=True, check=True
    )
    return [f for f in result.stdout.strip().split('\n') if f]


def should_scan(filepath: str) -> bool:
    """Determine if a file should be scanned."""
    p = Path(filepath)
    
    # Skip by extension
    if p.suffix.lower() in SKIP_EXTENSIONS:
        return False
    
    # Skip by path
    for skip in SKIP_PATHS:
        if skip in filepath.replace('\\', '/'):
            return False
    
    # Skip by filename
    if p.name in SKIP_FILES:
        return False
    
    return True


def get_staged_content(filepath: str) -> str:
    """Get the staged (not working tree) content of a file."""
    try:
        result = subprocess.run(
            ['git', 'show', f':{filepath}'],
            capture_output=True, check=True
        )
        content = result.stdout
        if len(content) > MAX_SCAN_SIZE:
            return ""  # Skip huge files
        try:
            return content.decode('utf-8', errors='ignore')
        except Exception:
            return ""
    except subprocess.CalledProcessError:
        return ""


def scan_file(filepath: str, content: str):
    """Scan one file for secret patterns. Return list of findings."""
    findings = []
    lines = content.split('\n')
    
    for pattern, description in PATTERNS:
        regex = re.compile(pattern)
        for line_num, line in enumerate(lines, 1):
            # Skip lines that are clearly comments or examples
            stripped = line.strip()
            if stripped.startswith('#') and 'SECRET' not in stripped.upper():
                # Skip but still check for the pattern (secrets in comments are still bad)
                pass
            
            if regex.search(line):
                # Get the matched text, masked
                match = regex.search(line)
                matched = match.group(0)
                # Mask the secret in output
                if len(matched) > 20:
                    masked = matched[:10] + '***' + matched[-5:]
                else:
                    masked = '***'
                
                findings.append({
                    'file': filepath,
                    'line': line_num,
                    'type': description,
                    'match': masked,
                })
    
    return findings


def main():
    staged = get_staged_files()
    
    if not staged:
        return 0  # Nothing to scan
    
    all_findings = []
    for f in staged:
        if not should_scan(f):
            continue
        content = get_staged_content(f)
        if content:
            findings = scan_file(f, content)
            all_findings.extend(findings)
    
    if not all_findings:
        return 0  # Clean
    
    # Print findings
    print("\n" + "=" * 70)
    print("🚨 CHARVAK PRE-COMMIT HOOK: SECRETS DETECTED")
    print("=" * 70)
    print(f"\n{len(all_findings)} potential secret(s) found in staged files:\n")
    
    for f in all_findings:
        print(f"  📄 {f['file']}:{f['line']}")
        print(f"     Type: {f['type']}")
        print(f"     Match: {f['match']}")
        print()
    
    print("=" * 70)
    print("⚠️  COMMIT BLOCKED")
    print("=" * 70)
    print("\nWhat to do:")
    print("  1. Move the secret to .env or a secure vault")
    print("  2. Use os.getenv('SECRET_NAME') instead of hardcoding")
    print("  3. Ensure .env is in .gitignore")
    print("  4. Re-stage your changes (git add)")
    print("  5. Try commit again")
    print()
    print("If this is a false positive (e.g., test fixture):")
    print("  • Add 'sk-XXX' to SKIP_FILES in .git/hooks/pre_commit_scanner.py")
    print("  • OR bypass this one time: git commit --no-verify")
    print()
    print("Learn more: see SECURITY.md in project root")
    print("=" * 70 + "\n")
    
    return 1  # Block commit


if __name__ == '__main__':
    sys.exit(main())