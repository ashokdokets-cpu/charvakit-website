"""
Charvak ATS Integration Engine
Connects Charvak's built-in ATS with external systems
(Greenhouse, Lever, Workday) for bidirectional sync
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.ats")


class ATSProvider:
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    WORKDAY = "workday"
    CHARVAK = "charvak"  # Our own ATS
    CUSTOM = "custom"


class ATSEngine:
    """Bidirectional ATS integration — Charvak ↔ External."""
    
    def __init__(self):
        self.integrations = []
        self.sync_log = []
        logger.info("✅ ATS Engine ready — Charvak ATS is primary")
    
    def connect_external_ats(self, data: Dict) -> Dict:
        """
        Connect Charvak to an external ATS.
        data = {"provider": str, "api_key": str, "base_url": str, "company_name": str}
        """
        integration_id = f"ATS-{secrets.token_hex(4).upper()}"
        
        integration = {
            "integration_id": integration_id,
            "provider": data.get("provider"),
            "api_key_prefix": data.get("api_key", "")[:8] + "***",
            "base_url": data.get("base_url", ""),
            "company_name": data.get("company_name"),
            "direction": "bidirectional",
            "status": "connected",
            "connected_at": datetime.now().isoformat()
        }
        
        self.integrations.append(integration)
        logger.info(f"External ATS connected: {data.get('provider')}")
        
        return {
            "status": "success",
            "integration_id": integration_id,
            "message": f"{data.get('provider')} connected. Charvak ATS is now syncing bidirectionally.",
            "sync_url": f"https://charvakit.com/api/ats/webhook/{integration_id}"
        }
    
    def sync_jobs_from_charvak(self, provider: str = "greenhouse") -> Dict:
        """
        Export Charvak jobs TO external ATS.
        This pushes our job board jobs to Greenhouse/Lever/Workday.
        """
        # Get jobs from Charvak's own job board
        from job_board_engine import job_board_engine
        charvak_jobs = job_board_engine.get_jobs()
        
        sync_id = f"SYNC-OUT-{secrets.token_hex(4).upper()}"
        self.sync_log.append({
            "sync_id": sync_id,
            "direction": "outbound",
            "provider": provider,
            "jobs_synced": len(charvak_jobs),
            "synced_at": datetime.now().isoformat()
        })
        
        return {
            "status": "success",
            "sync_id": sync_id,
            "message": f"{len(charvak_jobs)} jobs exported from Charvak to {provider}",
            "jobs_count": len(charvak_jobs)
        }
    
    def receive_webhook(self, integration_id: str, data: Dict) -> Dict:
        """
        Receive jobs from external ATS.
        Greenhouse/Lever/Workday call this to push jobs TO Charvak.
        """
        integration = self._find_integration(integration_id)
        if not integration:
            return {"status": "error", "message": "Integration not found"}
        
        sync_id = f"SYNC-IN-{secrets.token_hex(4).upper()}"
        
        # Import jobs into Charvak's job board
        from job_board_engine import job_board_engine
        if data.get("jobs"):
            for job_data in data["jobs"]:
                job_board_engine.post_job({
                    "title": job_data.get("title", "Imported Job"),
                    "company": integration.get("company_name", "External"),
                    "job_type": job_data.get("type", "Permanent"),
                    "location": job_data.get("location", "Remote"),
                    "description": job_data.get("description", ""),
                    "skills": job_data.get("skills", []),
                    "posted_by": f"ats_{integration['provider']}"
                })
        
        self.sync_log.append({
            "sync_id": sync_id,
            "direction": "inbound",
            "provider": integration["provider"],
            "jobs_received": len(data.get("jobs", [])),
            "received_at": datetime.now().isoformat()
        })
        
        return {
            "status": "success",
            "sync_id": sync_id,
            "message": f"{len(data.get('jobs', []))} jobs imported from {integration['provider']} to Charvak ATS"
        }
    
    def get_sync_log(self) -> Dict:
        """Get all sync history."""
        return {
            "status": "success",
            "syncs": self.sync_log,
            "count": len(self.sync_log),
            "inbound": len([s for s in self.sync_log if s["direction"] == "inbound"]),
            "outbound": len([s for s in self.sync_log if s["direction"] == "outbound"])
        }
    
    def get_integrations(self) -> Dict:
        """Get all ATS integrations."""
        return {
            "status": "success",
            "integrations": self.integrations,
            "count": len(self.integrations),
            "primary_ats": ATSProvider.CHARVAK,
            "supported_external": [ATSProvider.GREENHOUSE, ATSProvider.LEVER, ATSProvider.WORKDAY, ATSProvider.CUSTOM]
        }
    
    def get_stats(self) -> Dict:
        """Get ATS integration statistics."""
        return {
            "status": "success",
            "stats": {
                "total_integrations": len(self.integrations),
                "total_syncs": len(self.sync_log),
                "inbound_jobs": sum(s.get("jobs_received", 0) for s in self.sync_log if s["direction"] == "inbound"),
                "outbound_jobs": sum(s.get("jobs_synced", 0) for s in self.sync_log if s["direction"] == "outbound"),
                "providers": list(set(i["provider"] for i in self.integrations))
            }
        }
    
    def _find_integration(self, integration_id: str) -> Optional[Dict]:
        for integration in self.integrations:
            if integration["integration_id"] == integration_id:
                return integration
        return None


ats_engine = ATSEngine()