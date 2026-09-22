#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Download / update GeoLite2-City database.

Source: MaxMind GeoLite2 (via jsDelivr mirror of the community-maintained
npm package `geolite2-city`). No MaxMind license key required.

Run weekly via Render cron (schedule: 0 6 * * 3,5 = Wed & Fri).
Usage:
    python scripts/update_geoip.py
"""
import gzip
import os
import shutil
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

DB_URL = "https://cdn.jsdelivr.net/npm/geolite2-city/GeoLite2-City.mmdb.gz"
DB_PATH = Path("data/GeoLite2-City.mmdb")


def main():
    DB_PATH.parent.mkdir(exist_ok=True)
    print(f"[{datetime.utcnow().isoformat()}] Updating GeoLite2 DB...")
    print(f"  From: {DB_URL}")
    print(f"  To:   {DB_PATH}")

    tmp_gz = DB_PATH.with_suffix(".mmdb.gz.tmp")
    tmp_out = DB_PATH.with_suffix(".mmdb.new")

    try:
        # Download
        print("  Downloading...")
        req = urllib.request.Request(DB_URL, headers={"User-Agent": "Charvak-Update/1.0"})
        with urllib.request.urlopen(req, timeout=120) as resp, open(tmp_gz, "wb") as f_out:
            shutil.copyfileobj(resp, f_out, length=1024 * 1024)
        size_gz = tmp_gz.stat().st_size
        print(f"  Downloaded {size_gz:,} bytes (compressed)")

        # Decompress
        print("  Decompressing...")
        with gzip.open(tmp_gz, "rb") as f_in, open(tmp_out, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out, length=1024 * 1024)
        size_mmdb = tmp_out.stat().st_size
        print(f"  Decompressed {size_mmdb:,} bytes")

        # Atomic swap
        if DB_PATH.exists():
            DB_PATH.unlink()
        tmp_out.rename(DB_PATH)
        tmp_gz.unlink()
        print(f"  ✅ DB updated: {DB_PATH}")
        print(f"  Size: {size_mmdb / 1024 / 1024:.1f} MB")

        # Sanity check
        import geoip2.database
        reader = geoip2.database.Reader(str(DB_PATH))
        for test_ip in ["8.8.8.8", "49.36.0.0", "1.1.1.1"]:
            try:
                r = reader.city(test_ip)
                print(f"  {test_ip:<15} -> {r.country.iso_code} ({r.country.name})")
            except Exception as e:
                print(f"  {test_ip:<15} -> error: {e}")
        reader.close()
    except Exception as e:
        print(f"  ❌ Update failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
