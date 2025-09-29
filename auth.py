#!/usr/bin/env python3
"""
Zoom API Authentication Module
Handles OAuth token management with smart caching
"""

import base64
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel

logger = logging.getLogger("zoom-auth")


class ZoomConfig(BaseModel):
    """Configuration for Zoom API"""
    account_id: str
    client_id: str
    client_secret: str
    base_url: str = "https://api.zoom.us/v2"
    token_url: str = "https://zoom.us/oauth/token"


class TokenCache:
    """Smart token cache with expiry management"""
    
    def __init__(self):
        self.access_token: Optional[str] = None
        self.expires_at: Optional[datetime] = None
        self.created_at: Optional[datetime] = None
        
    def is_valid(self, buffer_minutes: int = 5) -> bool:
        """Check if token is valid with buffer time"""
        if not self.access_token or not self.expires_at:
            return False
        
        # Check if token expires within buffer time
        return datetime.now() < (self.expires_at - timedelta(minutes=buffer_minutes))
    
    def set_token(self, token: str, expires_in_seconds: int):
        """Cache new token with expiry time"""
        self.access_token = token
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(seconds=expires_in_seconds)
        
        logger.info(f"Token cached - Valid until: {self.expires_at.strftime('%H:%M:%S')}")
    
    def get_remaining_time(self) -> Optional[int]:
        """Get remaining time in minutes"""
        if not self.expires_at:
            return None
        
        remaining = self.expires_at - datetime.now()
        return max(0, int(remaining.total_seconds() / 60))
    
    def clear(self):
        """Clear cached token"""
        self.access_token = None
        self.expires_at = None
        self.created_at = None
        logger.info("Token cache cleared")


class ZoomAuth:
    """Zoom API Authentication Manager"""
    
    def __init__(self, config: ZoomConfig):
        self.config = config
        self.token_cache = TokenCache()
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
    
    async def get_access_token(self, force_refresh: bool = False) -> str:
        """Get access token - only generates new one if needed"""
        
        # Check if we have a valid cached token
        if not force_refresh and self.token_cache.is_valid():
            remaining = self.token_cache.get_remaining_time()
            logger.info(f"Using cached token - {remaining} minutes remaining")
            return self.token_cache.access_token
        
        # Generate new token
        logger.info("Generating new access token...")
        
        try:
            credentials = base64.b64encode(
                f"{self.config.client_id}:{self.config.client_secret}".encode()
            ).decode()
            
            headers = {
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "grant_type": "account_credentials",
                "account_id": self.config.account_id
            }
            
            response = await self.http_client.post(
                self.config.token_url,
                headers=headers,
                data=urlencode(data)
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get access token: {response.status_code} - {response.text}")
            
            token_data = response.json()
            
            # Cache the new token
            self.token_cache.set_token(
                token_data["access_token"], 
                token_data.get("expires_in", 3600)
            )
            
            logger.info("New access token generated successfully")
            return self.token_cache.access_token
            
        except Exception as e:
            logger.error(f"Error getting access token: {e}")
            raise
    
    async def ensure_valid_token(self) -> str:
        """Ensure we have a valid access token - smart caching"""
        return await self.get_access_token()
    
    async def get_auth_headers(self) -> dict:
        """Get authorization headers with valid token"""
        token = await self.ensure_valid_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def get_token_status(self) -> dict:
        """Get current token status for debugging"""
        if not self.token_cache.access_token:
            return {
                "status": "no_token",
                "message": "No token cached"
            }
        
        if self.token_cache.is_valid():
            remaining = self.token_cache.get_remaining_time()
            return {
                "status": "valid",
                "message": f"Token valid for {remaining} minutes",
                "remaining_minutes": remaining,
                "expires_at": self.token_cache.expires_at.isoformat() if self.token_cache.expires_at else None
            }
        else:
            return {
                "status": "expired",
                "message": "Token has expired",
                "expired_at": self.token_cache.expires_at.isoformat() if self.token_cache.expires_at else None
            }
    
    async def refresh_token(self) -> Dict[str, Any]:
        """Force refresh the access token"""
        await self.get_access_token(force_refresh=True)
        return self.get_token_status()