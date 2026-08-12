"""
Charvak SSO/SAML Authentication Engine
Enterprise SSO via SAML 2.0 (Okta, Azure AD, OneLogin, Google Workspace)
"""
import os
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional
from urllib.parse import urlencode

logger = logging.getLogger("charvakit.sso")

# SAML Configuration
SAML_ENABLED = os.getenv("SAML_ENABLED", "false").lower() == "true"
SAML_ENTITY_ID = os.getenv("SAML_ENTITY_ID", "https://charvakit.com/saml/metadata")
SAML_ACS_URL = os.getenv("SAML_ACS_URL", "https://charvakit.com/saml/acs")

# Pre-configured IdP metadata endpoints
SSO_PROVIDERS = {
    "okta": {
        "name": "Okta",
        "icon": "bi-shield-check",
        "color": "#007dc1",
        "metadata_url": os.getenv("OKTA_METADATA_URL", ""),
    },
    "azure": {
        "name": "Azure AD / Microsoft Entra",
        "icon": "bi-microsoft",
        "color": "#0078d4",
        "metadata_url": os.getenv("AZURE_METADATA_URL", ""),
    },
    "google": {
        "name": "Google Workspace",
        "icon": "bi-google",
        "color": "#4285f4",
        "metadata_url": os.getenv("GOOGLE_METADATA_URL", ""),
    },
    "onelogin": {
        "name": "OneLogin",
        "icon": "bi-box-arrow-in-right",
        "color": "#5b3cc4",
        "metadata_url": os.getenv("ONELOGIN_METADATA_URL", ""),
    },
}

# SSO sessions
sso_sessions = {}
sso_users = []


class SSOEngine:
    """Handles SAML 2.0 SSO for enterprise clients."""
    
    def __init__(self):
        self.enabled = SAML_ENABLED
        self.entity_id = SAML_ENTITY_ID
        self.acs_url = SAML_ACS_URL
        self.providers = SSO_PROVIDERS
        
        if self.enabled:
            logger.info("✅ SSO Engine: ENABLED")
            for key, provider in self.providers.items():
                if provider["metadata_url"]:
                    logger.info(f"   ↳ {provider['name']}: Configured")
        else:
            logger.info("⚠️ SSO Engine: DISABLED (set SAML_ENABLED=true to enable)")
    
    def get_configured_providers(self) -> Dict:
        """Get list of configured SSO providers."""
        active = {
            key: {"name": p["name"], "icon": p["icon"], "color": p["color"]}
            for key, p in self.providers.items()
            if p["metadata_url"] or not self.enabled  # Show all in dev mode
        }
        return {
            "status": "success",
            "enabled": self.enabled,
            "providers": active if active else self.providers
        }
    
    def generate_saml_request(self, provider_key: str, relay_state: str = "/") -> Dict:
        """
        Generate a SAML authentication request URL.
        In production, this creates a proper SAML AuthnRequest.
        """
        if provider_key not in self.providers:
            return {"status": "error", "message": f"Unknown provider: {provider_key}"}
        
        provider = self.providers[provider_key]
        request_id = f"SAML-{secrets.token_hex(8)}"
        
        # Store the request for callback
        sso_sessions[request_id] = {
            "request_id": request_id,
            "provider": provider_key,
            "relay_state": relay_state,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        # Production would create signed AuthnRequest XML
        # For now, redirect to IdP with proper parameters
        params = {
            "SAMLRequest": f"BASE64_AUTHN_REQUEST_{request_id}",
            "RelayState": relay_state,
            "entity_id": self.entity_id,
            "acs_url": self.acs_url
        }
        
        sso_url = f"{provider['metadata_url'].replace('/metadata', '')}/sso?{urlencode(params)}" if provider["metadata_url"] else ""
        
        logger.info(f"SAML Request generated: {request_id} for {provider_key}")
        
        return {
            "status": "success",
            "request_id": request_id,
            "sso_url": sso_url,
            "provider": provider["name"],
            "redirect": sso_url or f"/saml/login?provider={provider_key}&request={request_id}"
        }
    
    def handle_saml_response(self, saml_response: str, relay_state: str = "/") -> Dict:
        """
        Process SAML response from IdP.
        In production, this validates the SAML assertion and signature.
        """
        # Production would:
        # 1. Validate XML signature
        # 2. Parse SAML assertion
        # 3. Extract user attributes
        # 4. Verify conditions (timestamps, audience, etc.)
        
        # For now, simulate successful SSO
        user = {
            "email": f"sso-user-{secrets.token_hex(4)}@enterprise.com",
            "name": "SSO User",
            "role": "enterprise",
            "sso_provider": "saml",
            "authenticated_at": datetime.now().isoformat()
        }
        
        token = secrets.token_hex(32)
        sso_users.append({**user, "token": token})
        
        logger.info(f"SSO Login successful: {user['email']}")
        
        return {
            "status": "success",
            "token": token,
            "user": user,
            "redirect": relay_state
        }
    
    def get_sso_user(self, token: str) -> Optional[Dict]:
        """Get user from SSO token."""
        for user in sso_users:
            if user["token"] == token:
                return user
        return None
    
    def generate_metadata(self) -> Dict:
        """Generate SAML SP metadata XML for IdP configuration."""
        metadata = f"""<?xml version="1.0"?>
<md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
    entityID="{self.entity_id}">
    <md:SPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
        <md:AssertionConsumerService
            Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
            Location="{self.acs_url}"
            index="1"/>
    </md:SPSSODescriptor>
</md:EntityDescriptor>"""
        
        return {
            "status": "success",
            "entity_id": self.entity_id,
            "acs_url": self.acs_url,
            "metadata_xml": metadata,
            "setup_instructions": {
                "okta": "Create SAML 2.0 app in Okta admin → Enter ACS URL and Entity ID",
                "azure": "Add Enterprise Application in Azure AD → Setup SAML SSO",
                "google": "Add SAML app in Google Admin → Enter ACS URL and Entity ID",
                "onelogin": "Add SAML app in OneLogin → Enter ACS URL and Entity ID"
            }
        }


sso_engine = SSOEngine()