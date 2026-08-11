"""
Charvak Invoice Management System
Admin-controlled invoice generation with status tracking
"""
import os
import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional

INVOICE_FILE = "invoices.json"

class InvoiceStatus:
    DRAFT = "Draft"
    PENDING = "Pending - Not Sent"
    SENT = "Sent to Client"
    VIEWED = "Viewed by Client"
    PAID = "Paid"
    OVERDUE = "Overdue"
    CANCELLED = "Cancelled"

class InvoiceManager:
    """Complete invoice lifecycle management"""
    
    def __init__(self):
        self.invoices = self._load_invoices()
    
    def _load_invoices(self) -> Dict:
        try:
            with open(INVOICE_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_invoices(self):
        with open(INVOICE_FILE, 'w') as f:
            json.dump(self.invoices, f, indent=2, default=str)
    
    def create_invoice(self, admin_id: str, client_name: str, client_email: str,
                       service_type: str, amount: float, description: str = "",
                       due_days: int = 15) -> Dict:
        """Create a new invoice (Admin only)"""
        invoice_id = f"INV-{datetime.now().strftime('%Y%m')}-{secrets.token_hex(3).upper()}"
        invoice_number = f"CVK-{len(self.invoices) + 1:04d}"
        
        invoice = {
            "invoice_id": invoice_id,
            "invoice_number": invoice_number,
            "client_name": client_name,
            "client_email": client_email,
            "service_type": service_type,
            "description": description,
            "amount": amount,
            "gst_pct": 18,
            "gst_amount": round(amount * 0.18, 2),
            "total_amount": round(amount * 1.18, 2),
            "status": InvoiceStatus.DRAFT,
            "created_by": admin_id,
            "created_at": datetime.now().isoformat(),
            "due_date": (datetime.now() + timedelta(days=due_days)).isoformat(),
            "sent_at": None,
            "viewed_at": None,
            "paid_at": None,
            "history": [
                {"action": "Invoice Created", "timestamp": datetime.now().isoformat(), "by": admin_id}
            ]
        }
        
        self.invoices[invoice_id] = invoice
        self._save_invoices()
        
        return invoice
    
    def send_invoice(self, invoice_id: str, admin_id: str) -> Dict:
        """Mark invoice as sent to client"""
        if invoice_id not in self.invoices:
            return {"error": "Invoice not found"}
        
        self.invoices[invoice_id]["status"] = InvoiceStatus.SENT
        self.invoices[invoice_id]["sent_at"] = datetime.now().isoformat()
        self.invoices[invoice_id]["history"].append({
            "action": "Invoice Sent to Client",
            "timestamp": datetime.now().isoformat(),
            "by": admin_id
        })
        self._save_invoices()
        
        return self.invoices[invoice_id]
    
    def mark_paid(self, invoice_id: str, admin_id: str) -> Dict:
        """Mark invoice as paid"""
        if invoice_id not in self.invoices:
            return {"error": "Invoice not found"}
        
        self.invoices[invoice_id]["status"] = InvoiceStatus.PAID
        self.invoices[invoice_id]["paid_at"] = datetime.now().isoformat()
        self.invoices[invoice_id]["history"].append({
            "action": "Payment Received",
            "timestamp": datetime.now().isoformat(),
            "by": admin_id
        })
        self._save_invoices()
        
        return self.invoices[invoice_id]
    
    def cancel_invoice(self, invoice_id: str, admin_id: str, reason: str = "") -> Dict:
        """Cancel an invoice"""
        if invoice_id not in self.invoices:
            return {"error": "Invoice not found"}
        
        self.invoices[invoice_id]["status"] = InvoiceStatus.CANCELLED
        self.invoices[invoice_id]["history"].append({
            "action": f"Cancelled: {reason}",
            "timestamp": datetime.now().isoformat(),
            "by": admin_id
        })
        self._save_invoices()
        
        return self.invoices[invoice_id]
    
    def get_invoice(self, invoice_id: str) -> Optional[Dict]:
        """Get a specific invoice"""
        return self.invoices.get(invoice_id)
    
    def get_all_invoices(self, status: str = None) -> List[Dict]:
        """Get all invoices, optionally filtered by status"""
        invoices = list(self.invoices.values())
        if status:
            invoices = [i for i in invoices if i["status"] == status]
        return sorted(invoices, key=lambda x: x["created_at"], reverse=True)
    
    def get_client_invoices(self, client_email: str) -> List[Dict]:
        """Get invoices for a specific client"""
        return [i for i in self.invoices.values() if i["client_email"] == client_email]
    
    def get_invoice_stats(self) -> Dict:
        """Get invoice statistics"""
        all_invoices = list(self.invoices.values())
        total = len(all_invoices)
        total_amount = sum(i["total_amount"] for i in all_invoices)
        paid_amount = sum(i["total_amount"] for i in all_invoices if i["status"] == InvoiceStatus.PAID)
        pending_amount = sum(i["total_amount"] for i in all_invoices if i["status"] in [InvoiceStatus.SENT, InvoiceStatus.PENDING])
        
        return {
            "total_invoices": total,
            "total_amount": round(total_amount, 2),
            "paid_amount": round(paid_amount, 2),
            "pending_amount": round(pending_amount, 2),
            "by_status": {
                status: len([i for i in all_invoices if i["status"] == status])
                for status in [InvoiceStatus.DRAFT, InvoiceStatus.PENDING, InvoiceStatus.SENT, 
                              InvoiceStatus.PAID, InvoiceStatus.OVERDUE, InvoiceStatus.CANCELLED]
            }
        }
    
    def check_overdue(self):
        """Mark overdue invoices"""
        now = datetime.now()
        for inv in self.invoices.values():
            if inv["status"] in [InvoiceStatus.SENT, InvoiceStatus.PENDING]:
                due_date = datetime.fromisoformat(inv["due_date"])
                if now > due_date:
                    inv["status"] = InvoiceStatus.OVERDUE
        self._save_invoices()

# Initialize
invoice_manager = InvoiceManager()