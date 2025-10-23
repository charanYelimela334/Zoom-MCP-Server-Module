#!/usr/bin/env python3
"""
Zoom API Authentication Module with File-based Token Caching
FIXED: Timezone-aware datetime comparisons
"""

import base64
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from urllib.parse import urlencode
import os

import httpx
from pydantic import BaseModel

# Logger setup
logger = logging.getLogger("zoom-auth")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))


class ZoomConfig(BaseModel):
    """Configuration for Zoom API"""
    account_id: str
    client_id: str
    client_secret: str
    base_url: str = "https://api.zoom.us/v2"
    token_url: str = "https://zoom.us/oauth/token"
    token_file: str = r"D:\zoom-webinar\Access Token.txt"  # Your token file path


class FileTokenCache:
    """File-based token cache"""

    def __init__(self, token_file: str):
        self.token_file = token_file
        self.access_token: Optional[str] = None
        self.expires_at: Optional[datetime] = None
        self._load_from_file()

    def _load_from_file(self):
        if not os.path.exists(self.token_file):
            logger.info(f"Token file does not exist yet: {self.token_file}")
            return
        try:
            with open(self.token_file, "r") as f:
                content = f.read()
                if not content:
                    logger.warning(f"Token file is empty: {self.token_file}")
                    return
                    
                data = json.loads(content)
                self.access_token = data.get("access_token")
                expires_at_str = data.get("expires_at")
                if expires_at_str:
                    self.expires_at = datetime.fromisoformat(expires_at_str)
                logger.info(f"✅ Token loaded from file successfully")
        except Exception as e:
            logger.warning(f"Failed to read token file: {e}")

    def _save_to_file(self):
        try:
            logger.info(f"💾 Attempting to save token to: {self.token_file}")
            
            # Ensure directory exists
            dir_path = os.path.dirname(self.token_file)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
                logger.info(f"Created directory: {dir_path}")
            
            # Convert to IST for display
            expires_at_ist = self.expires_at.astimezone(IST) if self.expires_at else None
            
            data = {
                "access_token": self.access_token,
                "expires_at": self.expires_at.isoformat() if self.expires_at else None,
                "expires_at_ist": expires_at_ist.strftime("%Y-%m-%d %I:%M:%S %p IST") if expires_at_ist else None,
                "generated_at_ist": datetime.now(IST).strftime("%Y-%m-%d %I:%M:%S %p IST")
            }
            
            with open(self.token_file, "w") as f:
                json.dump(data, f, indent=2)
            
            # Verify the write
            file_size = os.path.getsize(self.token_file)
            logger.info(f"✅ Token saved successfully! File size: {file_size} bytes")
            logger.info(f"🕐 Expires at (IST): {data['expires_at_ist']}")
            
        except Exception as e:
            logger.error(f"❌ Failed to write token file: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def is_valid(self, buffer_minutes: int = 5) -> bool:
        """Check if token is valid. FIXED: Proper timezone-aware comparison."""
        if not self.access_token or not self.expires_at:
            return False
        
        # Ensure expires_at is timezone-aware (UTC)
        expires_at_utc = self.expires_at
        if expires_at_utc.tzinfo is None:
            # If naive, assume UTC
            expires_at_utc = expires_at_utc.replace(tzinfo=timezone.utc)
        
        # Get current time in UTC (timezone-aware)
        now_utc = datetime.now(timezone.utc)
        
        # Compare with buffer
        return now_utc < (expires_at_utc - timedelta(minutes=buffer_minutes))

    def set_token(self, token: str, expires_in_seconds: int):
        self.access_token = token
        self.expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in_seconds)
        self._save_to_file()
        
        # Log in IST
        expires_at_ist = self.expires_at.astimezone(IST)
        logger.info(f"Token cached - Valid until: {expires_at_ist.strftime('%I:%M:%S %p IST')}")

    def get_remaining_time(self) -> Optional[int]:
        if not self.expires_at:
            return None
        
        # Ensure expires_at is timezone-aware
        expires_at_utc = self.expires_at
        if expires_at_utc.tzinfo is None:
            expires_at_utc = expires_at_utc.replace(tzinfo=timezone.utc)
        
        now_utc = datetime.now(timezone.utc)
        remaining = expires_at_utc - now_utc
        return max(0, int(remaining.total_seconds() / 60))

    def clear(self):
        self.access_token = None
        self.expires_at = None
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
        logger.info("Token cache cleared")


class ZoomAuth:
    """Zoom API Authentication Manager with file-based token caching"""

    def __init__(self, config: ZoomConfig):
        self.config = config
        self.token_cache = FileTokenCache(config.token_file)
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()

    async def get_access_token(self, force_refresh: bool = False) -> str:
        """Get access token - use cached file token if valid"""
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
        return await self.get_access_token()

    async def get_auth_headers(self) -> Dict[str, str]:
        token = await self.ensure_valid_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def get_token_status(self) -> Dict[str, Any]:
        if not self.token_cache.access_token:
            return {"status": "no_token", "message": "No token cached"}
        if self.token_cache.is_valid():
            remaining = self.token_cache.get_remaining_time()
            expires_at_ist = self.token_cache.expires_at.astimezone(IST)
            return {
                "status": "valid", 
                "remaining_minutes": remaining,
                "expires_at_ist": expires_at_ist.strftime("%Y-%m-%d %I:%M:%S %p IST")
            }
        else:
            expires_at_ist = self.token_cache.expires_at.astimezone(IST)
            return {
                "status": "expired", 
                "expired_at": self.token_cache.expires_at.isoformat(),
                "expired_at_ist": expires_at_ist.strftime("%Y-%m-%d %I:%M:%S %p IST")
            }

    async def refresh_token(self) -> Dict[str, Any]:
        await self.get_access_token(force_refresh=True)
        return self.get_token_status()