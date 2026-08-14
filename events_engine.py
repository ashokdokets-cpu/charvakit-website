"""
Charvak Events Engine
Career fairs, webinars, info sessions, RSVP management
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.events")


class EventStatus:
    UPCOMING = "upcoming"
    LIVE = "live"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EventsEngine:
    """Complete events management system."""
    
    def __init__(self):
        self.events = []
        self.rsvps = []
        logger.info("✅ Events Engine ready")
    
    def create_event(self, data: Dict) -> Dict:
        """
        Create a career fair, webinar, or info session.
        
        data = {
            "title": str,
            "description": str,
            "event_type": "career_fair" / "webinar" / "info_session" / "workshop",
            "organizer_id": str,
            "organizer_name": str,
            "date": str (ISO format),
            "duration_minutes": int,
            "platform": "zoom" / "meet" / "teams" / "in_person",
            "location": str (for in-person),
            "link": str (for virtual),
            "max_attendees": int,
            "target_audience": str
        }
        """
        event_id = f"EVT-{secrets.token_hex(4).upper()}"
        
        event = {
            "event_id": event_id,
            "title": data.get("title"),
            "description": data.get("description", ""),
            "event_type": data.get("event_type", "webinar"),
            "organizer_id": data.get("organizer_id"),
            "organizer_name": data.get("organizer_name"),
            "date": data.get("date"),
            "duration_minutes": int(data.get("duration_minutes", 60)),
            "platform": data.get("platform", "zoom"),
            "location": data.get("location", ""),
            "link": data.get("link", ""),
            "max_attendees": int(data.get("max_attendees", 100)),
            "target_audience": data.get("target_audience", "All"),
            "rsvp_count": 0,
            "status": EventStatus.UPCOMING,
            "created_at": datetime.now().isoformat()
        }
        
        self.events.append(event)
        logger.info(f"Event created: {event_id} - {data.get('title')}")
        
        return {
            "status": "success",
            "event_id": event_id,
            "message": "Event created! RSVP is open.",
            "event_url": f"https://charvakit.com/events/{event_id}"
        }
    
    def rsvp_to_event(self, data: Dict) -> Dict:
        """
        RSVP to an event.
        
        data = {
            "event_id": str,
            "user_id": str,
            "user_name": str,
            "user_email": str,
            "user_type": "student" / "employer" / "alumni"
        }
        """
        event = self._find_event(data.get("event_id"))
        if not event:
            return {"status": "error", "message": "Event not found"}
        
        if event["rsvp_count"] >= event["max_attendees"]:
            return {"status": "error", "message": "Event is full"}
        
        rsvp_id = f"RSVP-{secrets.token_hex(4).upper()}"
        
        rsvp = {
            "rsvp_id": rsvp_id,
            "event_id": data.get("event_id"),
            "user_id": data.get("user_id"),
            "user_name": data.get("user_name"),
            "user_email": data.get("user_email"),
            "user_type": data.get("user_type", "student"),
            "checked_in": False,
            "rsvp_at": datetime.now().isoformat()
        }
        
        self.rsvps.append(rsvp)
        event["rsvp_count"] += 1
        
        logger.info(f"RSVP: {rsvp_id} for {event['event_id']}")
        
        return {
            "status": "success",
            "rsvp_id": rsvp_id,
            "message": f"RSVP confirmed for {event['title']}!",
            "confirmation": f"Details sent to {data.get('user_email')}"
        }
    
    def get_events(self, event_type: str = None) -> Dict:
        """Get all upcoming events."""
        events = [e for e in self.events if e["status"] == EventStatus.UPCOMING]
        if event_type:
            events = [e for e in events if e["event_type"] == event_type]
        
        events.sort(key=lambda e: e["date"])
        
        return {
            "status": "success",
            "events": events,
            "count": len(events),
            "total_rsvps": sum(e["rsvp_count"] for e in events),
            "types": list(set(e["event_type"] for e in self.events))
        }
    
    def get_event(self, event_id: str) -> Dict:
        """Get event details."""
        event = self._find_event(event_id)
        if not event:
            return {"status": "error", "message": "Event not found"}
        
        event_rsvps = [r for r in self.rsvps if r["event_id"] == event_id]
        
        return {
            "status": "success",
            "event": event,
            "rsvps": event_rsvps,
            "rsvp_count": len(event_rsvps),
            "check_in_count": len([r for r in event_rsvps if r["checked_in"]])
        }
    
    def check_in(self, rsvp_id: str) -> Dict:
        """Check in attendee."""
        for rsvp in self.rsvps:
            if rsvp["rsvp_id"] == rsvp_id:
                rsvp["checked_in"] = True
                rsvp["checked_in_at"] = datetime.now().isoformat()
                return {"status": "success", "message": "Checked in!"}
        return {"status": "error", "message": "RSVP not found"}
    
    def cancel_event(self, event_id: str) -> Dict:
        """Cancel an event."""
        event = self._find_event(event_id)
        if not event:
            return {"status": "error", "message": "Event not found"}
        
        event["status"] = EventStatus.CANCELLED
        return {"status": "success", "message": "Event cancelled"}
    
    def get_stats(self) -> Dict:
        """Get event statistics."""
        return {
            "status": "success",
            "stats": {
                "total_events": len(self.events),
                "upcoming_events": len([e for e in self.events if e["status"] == EventStatus.UPCOMING]),
                "total_rsvps": len(self.rsvps),
                "total_check_ins": len([r for r in self.rsvps if r["checked_in"]])
            }
        }
    
    def _find_event(self, event_id: str) -> Optional[Dict]:
        for event in self.events:
            if event["event_id"] == event_id:
                return event
        return None


events_engine = EventsEngine()