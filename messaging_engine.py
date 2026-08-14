"""
Charvak Messaging Engine
Direct messaging: Employer ↔ Candidate InMail system
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional
import secrets

logger = logging.getLogger("charvakit.messaging")


class MessageStatus:
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    REPLIED = "replied"


class MessagingEngine:
    """Complete messaging system for employers and candidates."""
    
    def __init__(self):
        self.messages = []
        self.conversations = []
        self.templates = self._seed_templates()
        logger.info("✅ Messaging Engine ready")
    
    def _seed_templates(self) -> List[Dict]:
        """Pre-built message templates."""
        return [
            {"id": "TPL-001", "name": "Interview Invitation", "body": "Hi {{name}}, we reviewed your profile and would love to invite you for an interview for the {{role}} position at {{company}}. Are you available this week?"},
            {"id": "TPL-002", "name": "Job Opportunity", "body": "Hi {{name}}, I came across your profile and think you'd be a great fit for our {{role}} position. Interested?"},
            {"id": "TPL-003", "name": "Application Update", "body": "Hi {{name}}, thank you for applying to {{company}}. Your application is under review. We'll update you within 48 hours."},
            {"id": "TPL-004", "name": "Offer Extension", "body": "Hi {{name}}, congratulations! We'd like to extend an offer for the {{role}} position. Let's discuss details."},
            {"id": "TPL-005", "name": "Rejection - Soft", "body": "Hi {{name}}, thank you for your interest. While your profile is impressive, we've decided to move forward with other candidates. We'll keep you in mind for future roles."},
        ]
    
    def send_message(self, data: Dict) -> Dict:
        """
        Send a message.
        
        data = {
            "sender_id": str,
            "sender_type": "employer" or "candidate",
            "recipient_id": str,
            "recipient_type": "employer" or "candidate",
            "subject": str,
            "body": str,
            "template_id": str (optional),
            "job_id": str (optional),
            "application_id": str (optional)
        }
        """
        message_id = f"MSG-{secrets.token_hex(4).upper()}"
        
        # Use template if provided
        body = data.get("body", "")
        if data.get("template_id"):
            template = self._find_template(data["template_id"])
            if template:
                body = template["body"].replace("{{name}}", data.get("recipient_name", ""))
                body = body.replace("{{role}}", data.get("role", ""))
                body = body.replace("{{company}}", data.get("company", ""))
        
        message = {
            "message_id": message_id,
            "sender_id": data.get("sender_id"),
            "sender_type": data.get("sender_type"),
            "recipient_id": data.get("recipient_id"),
            "recipient_type": data.get("recipient_type"),
            "subject": data.get("subject", "New Message"),
            "body": body,
            "job_id": data.get("job_id"),
            "application_id": data.get("application_id"),
            "status": MessageStatus.SENT,
            "created_at": datetime.now().isoformat(),
            "read_at": None
        }
        
        self.messages.append(message)
        self._update_conversation(message)
        
        logger.info(f"Message sent: {message_id} from {data.get('sender_id')} to {data.get('recipient_id')}")
        
        return {
            "status": "success",
            "message_id": message_id,
            "message": "Message sent successfully"
        }
    
    def _update_conversation(self, message: Dict):
        """Update or create conversation thread."""
        convo_key = f"{message['sender_id']}:{message['recipient_id']}"
        convo_key_rev = f"{message['recipient_id']}:{message['sender_id']}"
        
        for convo in self.conversations:
            if convo["key"] == convo_key or convo["key"] == convo_key_rev:
                convo["messages"].append(message)
                convo["last_message"] = message
                convo["updated_at"] = datetime.now().isoformat()
                return
        
        self.conversations.append({
            "key": convo_key,
            "participants": [message["sender_id"], message["recipient_id"]],
            "messages": [message],
            "last_message": message,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        })
    
    def get_inbox(self, user_id: str) -> Dict:
        """Get user's inbox."""
        user_conversations = []
        for convo in self.conversations:
            if user_id in convo["participants"]:
                user_conversations.append({
                    "conversation_key": convo["key"],
                    "participants": convo["participants"],
                    "last_message": convo["last_message"],
                    "message_count": len(convo["messages"]),
                    "unread_count": len([m for m in convo["messages"] if m["status"] != MessageStatus.READ and m["recipient_id"] == user_id]),
                    "updated_at": convo["updated_at"]
                })
        
        user_conversations.sort(key=lambda c: c["updated_at"], reverse=True)
        
        return {
            "status": "success",
            "conversations": user_conversations,
            "count": len(user_conversations),
            "total_unread": sum(c["unread_count"] for c in user_conversations)
        }
    
    def get_conversation(self, user_id: str, other_user_id: str) -> Dict:
        """Get full conversation between two users."""
        convo_key = f"{user_id}:{other_user_id}"
        convo_key_rev = f"{other_user_id}:{user_id}"
        
        for convo in self.conversations:
            if convo["key"] == convo_key or convo["key"] == convo_key_rev:
                # Mark as read
                for msg in convo["messages"]:
                    if msg["recipient_id"] == user_id and msg["status"] != MessageStatus.READ:
                        msg["status"] = MessageStatus.READ
                        msg["read_at"] = datetime.now().isoformat()
                return {"status": "success", "conversation": convo}
        
        return {"status": "error", "message": "Conversation not found"}
    
    def mark_read(self, message_id: str) -> Dict:
        """Mark a message as read."""
        for msg in self.messages:
            if msg["message_id"] == message_id:
                msg["status"] = MessageStatus.READ
                msg["read_at"] = datetime.now().isoformat()
                return {"status": "success", "message": "Marked as read"}
        return {"status": "error", "message": "Message not found"}
    
    def get_templates(self) -> Dict:
        """Get all message templates."""
        return {"status": "success", "templates": self.templates, "count": len(self.templates)}
    
    def get_stats(self) -> Dict:
        """Get messaging statistics."""
        return {
            "status": "success",
            "stats": {
                "total_messages": len(self.messages),
                "total_conversations": len(self.conversations),
                "unread_messages": len([m for m in self.messages if m["status"] == MessageStatus.SENT or m["status"] == MessageStatus.DELIVERED]),
                "read_messages": len([m for m in self.messages if m["status"] == MessageStatus.READ]),
                "active_conversations": len([c for c in self.conversations if len(c["messages"]) > 1])
            }
        }
    
    def _find_template(self, template_id: str) -> Optional[Dict]:
        for template in self.templates:
            if template["id"] == template_id:
                return template
        return None


messaging_engine = MessagingEngine()