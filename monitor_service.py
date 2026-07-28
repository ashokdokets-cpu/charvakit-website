"""
Charvakit Silent-Killer Monitor Service
Background monitoring for websites, webhooks, and APIs
"""
import os
import json
import time
import httpx
import asyncio
from datetime import datetime
from typing import Dict, List

# Store monitored sites (in production, use database)
monitored_sites = {}
alert_history = []

class SiteMonitor:
    def __init__(self, url: str, name: str, check_interval: int = 300):
        self.url = url
        self.name = name
        self.interval = check_interval  # seconds
        self.last_check = None
        self.status = "unknown"
        self.issues = []
    
    async def check_site(self):
        """Check website health"""
        issues = []
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                start = time.time()
                response = await client.get(self.url)
                response_time = time.time() - start
                
                # Check HTTP status
                if response.status_code >= 400:
                    issues.append(f"HTTP {response.status_code}")
                
                # Check response time
                if response_time > 3:
                    issues.append(f"Slow response: {response_time:.1f}s")
                
                # Check for common issues
                content = response.text.lower()
                if "error" in content and "error handling" not in content:
                    issues.append("Error text detected on page")
                
        except Exception as e:
            issues.append(f"Connection failed: {str(e)}")
        
        self.last_check = datetime.now().isoformat()
        self.status = "healthy" if not issues else "issues_detected"
        self.issues = issues
        
        if issues:
            alert_history.append({
                "url": self.url,
                "name": self.name,
                "issues": issues,
                "time": self.last_check
            })
        
        return {"status": self.status, "issues": issues, "checked_at": self.last_check}

# Global monitor instance
monitor = SiteMonitor("", "")

async def add_monitor(url: str, name: str, interval: int = 300) -> Dict:
    """Add a site to monitor"""
    monitored_sites[url] = SiteMonitor(url, name, interval)
    return {"status": "added", "url": url, "name": name, "interval": interval}

async def check_all_sites() -> List[Dict]:
    """Check all monitored sites"""
    results = []
    for url, monitor in monitored_sites.items():
        result = await monitor.check_site()
        results.append(result)
    return results

async def get_monitor_status(url: str = None) -> Dict:
    """Get status of monitored sites"""
    if url and url in monitored_sites:
        m = monitored_sites[url]
        return {
            "url": url,
            "name": m.name,
            "status": m.status,
            "last_check": m.last_check,
            "issues": m.issues
        }
    
    return {
        "sites_monitored": len(monitored_sites),
        "total_alerts": len(alert_history),
        "recent_alerts": alert_history[-10:] if alert_history else [],
        "sites": {url: {"name": m.name, "status": m.status} for url, m in monitored_sites.items()}
    }

async def run_monitor_loop():
    """Background monitoring loop"""
    while True:
        await check_all_sites()
        await asyncio.sleep(300)  # Check every 5 minutes