"""
Session 47.5: Automated migration runner.

Runs all idempotent migrations against the target DATABASE_URL.
Safe to invoke at startup. Never blocks the app from booting.
"""
import glob
import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] migrations: %(message)s",
)
log = logging.getLogger("migrations")


def main() -> int:
    url = os.getenv("DATABASE_URL", "")
    if not url:
        log.error("No DATABASE_URL — skipping migration")
        return 0

    host = url.split("@")[1].split("/")[0] if "@" in url else "unknown"
    is_prod = "render.com" in host or "singapore" in host
    log.info(f"Target DB host: {host} (prod={is_prod})")

    try:
        import psycopg2
    except ImportError:
        log.error("psycopg2 not installed — skipping migration")
        return 0

    files = sorted(glob.glob("migrations/*.sql"))
    if not files:
        log.info("No migration files found — nothing to do")
        return 0

    log.info(f"Found {len(files)} migration files")

    try:
        conn = psycopg2.connect(url)
        conn.autocommit = False
        cur = conn.cursor()
    except Exception as e:
        log.error(f"Cannot connect to DB: {e}")
        return 0

    applied = 0
    skipped = 0
    failed = 0

    for path in files:
        name = os.path.basename(path)
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                sql = f.read()
            if not sql.strip():
                log.info(f"  skip  {name} (empty)")
                skipped += 1
                continue
            cur.execute(sql)
            conn.commit()
            log.info(f"  ok    {name}")
            applied += 1
        except Exception as e:
            try:
                conn.rollback()
            except Exception:
                pass
            err_short = str(e).split("\n")[0][:200]
            log.warning(f"  warn  {name}: {err_short}")
            failed += 1

    try:
        cur.close()
        conn.close()
    except Exception:
        pass

    log.info(
        f"Migration summary: applied={applied} skipped={skipped} "
        f"failed_or_already_exists={failed} total={len(files)}"
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        log.error(f"Migration runner crashed unexpectedly: {e}")
        sys.exit(0)