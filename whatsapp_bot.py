"""
Charvak Voice-to-Web WhatsApp Bot
Handles voice note intake, processes audio, and triggers AI website generation
"""
import os
import json
import requests
from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
import openai
from typing import Optional

# Configuration
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "your_whatsapp_token")
WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "your_phone_id")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_key")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "charvak_voice_web_2024")

# Supported languages
SUPPORTED_LANGUAGES = [
    "en", "hi", "te", "ta", "kn", "ml", "mr", "bn", "gu", "pa",
    "es", "fr", "de", "pt", "ar", "ja", "ko", "zh", "ru", "it",
    "nl", "tr", "vi", "th", "id", "ms", "fil", "sw", "am", "ha",
    "yo", "ig", "zu", "so"
]

async def send_whatsapp_message(to: str, message: str):
    """Send a WhatsApp message via Meta API"""
    url = f"https://graph.facebook.com/v18.0/{WHATSAPP_PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

async def process_voice_note(media_url: str, media_id: str):
    """Download and transcribe voice note using OpenAI Whisper"""
    # Download media from WhatsApp
    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
    audio_response = requests.get(media_url, headers=headers)
    
    # Save temporarily
    audio_path = f"temp_{media_id}.ogg"
    with open(audio_path, "wb") as f:
        f.write(audio_response.content)
    
    # Transcribe with Whisper
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="text"
        )
    
    # Clean up
    os.remove(audio_path)
    return transcript

async def generate_website_from_voice(transcript: str, language: str, user_phone: str):
    """AI generates website structure from voice transcript"""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    prompt = f"""
    You are Charvak Voice-to-Web AI. Parse this business description and generate:
    1. Business name
    2. Category (restaurant, plumbing, salon, retail, clinic, etc.)
    3. Services/products with prices
    4. Contact info
    5. Business hours
    6. Location
    7. Key features to highlight
    
    Business description (in {language}): {transcript}
    
    Return as JSON.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    business_data = json.loads(response.choices[0].message.content)
    
    # Generate website HTML
    website_prompt = f"""
    Generate a complete, mobile-optimized HTML website for this business:
    {json.dumps(business_data, indent=2)}
    
    Include:
    - Modern Tailwind CSS styling
    - Hero section with business name
    - Services/products with prices
    - Contact section with WhatsApp button
    - Business hours
    - Location/Map link
    - Professional color scheme
    - Responsive design
    - PWA manifest
    
    Return complete HTML with inline CSS.
    """
    
    website_response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": website_prompt}]
    )
    
    website_html = website_response.choices[0].message.content
    
    # Save website
    site_id = f"vtw_{user_phone.replace('+', '')}_{int(time.time())}"
    site_path = f"static/sites/{site_id}.html"
    os.makedirs("static/sites", exist_ok=True)
    with open(site_path, "w", encoding="utf-8") as f:
        f.write(website_html)
    
    return {
        "site_id": site_id,
        "url": f"/sites/{site_id}",
        "business_data": business_data
    }

# WhatsApp Webhook Handler
async def handle_whatsapp_webhook(data: dict):
    """Process incoming WhatsApp messages"""
    if "entry" not in data:
        return
    
    for entry in data["entry"]:
        for change in entry.get("changes", []):
            value = change.get("value", {})
            messages = value.get("messages", [])
            
            for message in messages:
                user_phone = message["from"]
                
                # Handle voice note
                if message.get("type") == "audio":
                    media_id = message["audio"]["id"]
                    
                    # Get media URL
                    url = f"https://graph.facebook.com/v18.0/{media_id}"
                    headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}
                    media_response = requests.get(url, headers=headers).json()
                    media_url = media_response.get("url")
                    
                    # Send processing message
                    await send_whatsapp_message(
                        user_phone,
                        "🎙️ Voice note received! Transcribing and building your website... (1-2 minutes)"
                    )
                    
                    # Process voice note
                    transcript = await process_voice_note(media_url, media_id)
                    
                    # Generate website
                    site_data = await generate_website_from_voice(
                        transcript, "auto", user_phone
                    )
                    
                    # Send result
                    site_url = f"https://www.charvakit.com{site_data['url']}"
                    await send_whatsapp_message(
                        user_phone,
                        f"✅ Your website is ready!\n\n🔗 {site_url}\n\n📱 Share this link anywhere!\n\n💡 Upgrade to Pro for custom domain and AI webmaster support."
                    )
                
                # Handle text message
                elif message.get("type") == "text":
                    text = message["text"]["body"].lower()
                    
                    if text in ["hi", "hello", "start", "help"]:
                        await send_whatsapp_message(
                            user_phone,
                            "👋 Welcome to Charvak Voice-to-Web!\n\n"
                            "🎙️ Send a voice note describing your business, and I'll build your website in 3 minutes!\n\n"
                            "📝 Include:\n"
                            "- Your business name\n"
                            "- What you do/sell\n"
                            "- Prices (if any)\n"
                            "- Location\n"
                            "- Contact info\n\n"
                            "🌐 Speak in any of 34 languages!\n"
                            "💰 Free to build. Pro plans start at ₹499/mo."
                        )
                    elif text in ["pricing", "price", "cost", "pro"]:
                        await send_whatsapp_message(
                            user_phone,
                            "💎 Charvak Voice-to-Web Pricing:\n\n"
                            "🆓 Free: AI website generation, basic template\n"
                            "⭐ Pro (₹499/mo): Custom domain, no branding, AI SEO, on-demand updates\n\n"
                            "🎉 Beta offer: First 100 businesses get 3 months Pro FREE!\n"
                            "Reply 'BETA' to claim."
                        )
                    elif text == "beta":
                        await send_whatsapp_message(
                            user_phone,
                            "🎉 You're on the beta list! Send your first voice note to get started.\n\n"
                            "We'll notify you when your free Pro upgrade is activated."
                        )
                    else:
                        await send_whatsapp_message(
                            user_phone,
                            "Send a 🎙️ voice note describing your business to build your website!\n\n"
                            "Or type:\n"
                            "- PRICING for plan details\n"
                            "- BETA for free Pro access"
                        )

# Export handler for main.py integration
whatsapp_handler = handle_whatsapp_webhook