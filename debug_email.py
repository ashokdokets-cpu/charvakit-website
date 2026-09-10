from email_engine import email_engine
import os

print(f"SendGrid Key: {os.getenv('SENDGRID_API_KEY', 'NOT SET')[:20]}...")
print(f"Email enabled: {email_engine.enabled}")

# Try to send a real test
result = email_engine.send_email(
    "hr@charvakit.com",
    "Charvak Email Test",
    "Testing email delivery from Charvak."
)
print(f"\nResult: {result}")

# Check actual SendGrid response
import requests
import json

api_key = os.getenv('SENDGRID_API_KEY', '')
if api_key:
    sg_response = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "personalizations": [{"to": [{"email": "hr@charvakit.com"}]}],
            "from": {"email": "hr@charvakit.com", "name": "Charvak"},
            "subject": "Test Email",
            "content": [{"type": "text/plain", "value": "Test"}]
        }
    )
    print(f"\nSendGrid Status: {sg_response.status_code}")
    if sg_response.status_code != 202:
        print(f"SendGrid Error: {sg_response.text}")
