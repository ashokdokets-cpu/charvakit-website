"""
Charvak notification retention cleanup.

Deletes charvak_notifications rows older than N days (default: 90).

Run manually:   python scripts/cleanup_notifications.py
Dry run:        python scripts/cleanup_notifications.py --dry-run
Custom days:    python scripts/cleanup_notifications.py --days 30
Run on Render:  cron job, weekly

Environment:
    NOTIFICATION_RETENTION_DAYS    (default 90)
"""
import argparse
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db


def cleanup(days=90, dry_run=False):
    """Delete notifications older than `days` days. Return count."""
    cutoff = datetime.now() - timedelta(days=days)

    conn = db.get_connection()
    cur = conn.cursor()

    # Count first (also serves as dry-run report)
    cur.execute("""
        SELECT COUNT(*) FROM charvak_notifications
        WHERE sent_at < %s
    """, (cutoff,))
    count = int(cur.fetchone()[0] or 0)

    print(f"Cutoff: {cutoff.isoformat()}  ({days} days ago)")
    print(f"Rows to delete: {count}")

    if dry_run or count == 0:
        cur.close()
        conn.close()
        print("[DRY RUN]" if dry_run else "[NOOP]")
        return count

    # Show breakdown by status before delete
    cur.execute("""
        SELECT status, COUNT(*) FROM charvak_notifications
        WHERE sent_at < %s
        GROUP BY status
    """, (cutoff,))
    print("\nBreakdown by status:")
    for status, n in cur.fetchall():
        print(f"  {status}: {n}")

    # Delete
    cur.execute("DELETE FROM charvak_notifications WHERE sent_at < %s", (cutoff,))
    deleted = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()

    print(f"\nDeleted {deleted} rows.")
    return deleted


def main():
    parser = argparse.ArgumentParser(description="Cleanup old notifications")
    parser.add_argument("--days", type=int,
                        default=int(os.environ.get("NOTIFICATION_RETENTION_DAYS", 90)),
                        help="Delete notifications older than N days (default: 90)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be deleted without deleting")
    args = parser.parse_args()

    print(f"=== Notification cleanup ===")
    print(f"Days: {args.days}")
    print(f"Dry run: {args.dry_run}")
    print()

    cleanup(days=args.days, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
