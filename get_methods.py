#!/usr/bin/env python3
"""
Zoom API GET Methods Module
Handles all GET operations for webinars
"""

import logging
from typing import Any, Dict, List, Optional

import httpx

from auth import ZoomAuth

logger = logging.getLogger("zoom-get")


class ZoomGetMethods:
    """Handles all GET operations for Zoom webinars"""
    
    def __init__(self, auth: ZoomAuth):
        self.auth = auth
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
    
    async def list_webinars(self, user_id: str, page_size: int = 30, page_number: int = 1) -> Dict[str, Any]:
        """List webinars for a user"""
        try:
            headers = await self.auth.get_auth_headers()
            
            params = {
                "page_size": page_size,
                "page_number": page_number
            }
            
            response = await self.http_client.get(
                f"{self.auth.config.base_url}/users/{user_id}/webinars",
                headers=headers,
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to list webinars: {response.status_code} - {response.text}")
            
            result = response.json()
            logger.info(f"Retrieved {len(result.get('webinars', []))} webinars for user: {user_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error listing webinars: {e}")
            raise
    
    async def get_webinar(self, webinar_id: str, occurrence_id: str = None, show_previous_occurrences: bool = False) -> Dict[str, Any]:
        """Get details of a specific webinar"""
        try:
            headers = await self.auth.get_auth_headers()
            
            params = {}
            if occurrence_id:
                params["occurrence_id"] = occurrence_id
            if show_previous_occurrences:
                params["show_previous_occurrences"] = "true"
            
            response = await self.http_client.get(
                f"{self.auth.config.base_url}/webinars/{webinar_id}",
                headers=headers,
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get webinar: {response.status_code} - {response.text}")
            
            result = response.json()
            logger.info(f"Retrieved webinar details: {webinar_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting webinar: {e}")
            raise
    
    async def get_webinar_absentees(self, webinar_uuid: str, occurrence_id: str = None, page_size: int = 30, page_number: int = 1) -> Dict[str, Any]:
        """Get webinar absentees (registrants who did not attend)"""
        try:
            headers = await self.auth.get_auth_headers()
            
            params = {
                "page_size": page_size,
                "page_number": page_number
            }
            if occurrence_id:
                params["occurrence_id"] = occurrence_id
            
            response = await self.http_client.get(
                f"{self.auth.config.base_url}/past_webinars/{webinar_uuid}/absentees",
                headers=headers,
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get absentees: {response.status_code} - {response.text}")
            
            result = response.json()
            logger.info(f"Retrieved absentees for webinar: {webinar_uuid}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting absentees: {e}")
            raise
    
    async def list_webinar_participants(self, webinar_uuid: str, occurrence_id: str = None, page_size: int = 30, page_number: int = 1) -> Dict[str, Any]:
        """List participants of a past webinar"""
        try:
            headers = await self.auth.get_auth_headers()
            
            params = {
                "page_size": page_size,
                "page_number": page_number
            }
            if occurrence_id:
                params["occurrence_id"] = occurrence_id
            
            response = await self.http_client.get(
                f"{self.auth.config.base_url}/past_webinars/{webinar_uuid}/participants",
                headers=headers,
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to list participants: {response.status_code} - {response.text}")
            
            result = response.json()
            logger.info(f"Retrieved participants for webinar: {webinar_uuid}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error listing participants: {e}")
            raise
    
    async def list_webinar_qa(self, webinar_uuid: str, occurrence_id: str = None) -> Dict[str, Any]:
        """List Q&A of a past webinar"""
        try:
            headers = await self.auth.get_auth_headers()
            
            params = {}
            if occurrence_id:
                params["occurrence_id"] = occurrence_id
            
            response = await self.http_client.get(
                f"{self.auth.config.base_url}/past_webinars/{webinar_uuid}/qa",
                headers=headers,
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to list Q&A: {response.status_code} - {response.text}")
            
            result = response.json()
            logger.info(f"Retrieved Q&A for webinar: {webinar_uuid}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error listing Q&A: {e}")
            raise
    
    async def list_panelists(self, webinar_id: str) -> Dict[str, Any]:
        """List panelists of a webinar"""
        try:
            headers = await self.auth.get_auth_headers()
            
            response = await self.http_client.get(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/panelists",
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to list panelists: {response.status_code} - {response.text}")
            
            result = response.json()
            logger.info(f"Retrieved panelists for webinar: {webinar_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error listing panelists: {e}")
            raise
    
    async def get_webinar_registrant(self, webinar_id: str, registrant_id: str, occurrence_id: str = None) -> Dict[str, Any]:
        """Get a specific webinar registrant"""
        try:
            headers = await self.auth.get_auth_headers()
            
            params = {}
            if occurrence_id:
                params["occurrence_id"] = occurrence_id
            
            response = await self.http_client.get(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/registrants/{registrant_id}",
                headers=headers,
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get registrant: {response.status_code} - {response.text}")
            
            result = response.json()
            logger.info(f"Retrieved registrant {registrant_id} for webinar: {webinar_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting registrant: {e}")
            raise
    
    async def list_registration_questions(self, webinar_id: str) -> Dict[str, Any]:
        """List registration questions for a webinar"""
        try:
            headers = await self.auth.get_auth_headers()
            
            response = await self.http_client.get(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/registrants/questions",
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to list registration questions: {response.status_code} - {response.text}")
            
            result = response.json()
            logger.info(f"Retrieved registration questions for webinar: {webinar_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error listing registration questions: {e}")
            raise
    
    async def list_webinar_registrants(self, webinar_id: str, occurrence_id: str = None, status: str = "approved", page_size: int = 30, page_number: int = 1) -> Dict[str, Any]:
        """List webinar registrants"""
        try:
            headers = await self.auth.get_auth_headers()
            
            params = {
                "status": status,
                "page_size": page_size,
                "page_number": page_number
            }
            if occurrence_id:
                params["occurrence_id"] = occurrence_id
            
            response = await self.http_client.get(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/registrants",
                headers=headers,
                params=params
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to list registrants: {response.status_code} - {response.text}")
            
            result = response.json()
            logger.info(f"Retrieved registrants for webinar: {webinar_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error listing registrants: {e}")
            raise
    
    async def get_webinar_polls(self, webinar_id: str) -> Dict[str, Any]:
        """Get polls for a webinar"""
        try:
            headers = await self.auth.get_auth_headers()
            
            response = await self.http_client.get(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/polls",
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get polls: {response.status_code} - {response.text}")
            
            result = response.json()
            logger.info(f"Retrieved polls for webinar: {webinar_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting polls: {e}")
            raise
    
    async def get_webinar_poll(self, webinar_id: str, poll_id: str) -> Dict[str, Any]:
        """Get a specific poll for a webinar"""
        try:
            headers = await self.auth.get_auth_headers()
            
            response = await self.http_client.get(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/polls/{poll_id}",
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get poll: {response.status_code} - {response.text}")
            
            result = response.json()
            logger.info(f"Retrieved poll {poll_id} for webinar: {webinar_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting poll: {e}")
            raise
    
    async def get_webinar_survey(self, webinar_id: str) -> Dict[str, Any]:
        """Get survey for a webinar"""
        try:
            headers = await self.auth.get_auth_headers()
            
            response = await self.http_client.get(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/survey",
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get survey: {response.status_code} - {response.text}")
            
            result = response.json()
            logger.info(f"Retrieved survey for webinar: {webinar_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting survey: {e}")
            raise
    
    async def get_webinar_tracking_sources(self, webinar_id: str) -> Dict[str, Any]:
        """Get tracking sources for a webinar"""
        try:
            headers = await self.auth.get_auth_headers()
            
            response = await self.http_client.get(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/tracking_sources",
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get tracking sources: {response.status_code} - {response.text}")
            
            result = response.json()
            logger.info(f"Retrieved tracking sources for webinar: {webinar_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting tracking sources: {e}")
            raise
    
    async def get_users(self, user_id: Optional[str] = None, status: str = "active", page_size: int = 30, page_number: int = 1) -> Dict[str, Any]:
        """Get users from Zoom account"""
        try:
            headers = await self.auth.get_auth_headers()
            
            if user_id:
                # Get specific user
                response = await self.http_client.get(
                    f"{self.auth.config.base_url}/users/{user_id}",
                    headers=headers
                )
            else:
                # List all users
                params = {
                    "status": status,
                    "page_size": page_size,
                    "page_number": page_number
                }
                
                response = await self.http_client.get(
                    f"{self.auth.config.base_url}/users",
                    headers=headers,
                    params=params
                )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get users: {response.status_code} - {response.text}")
            
            result = response.json()
            logger.info("Users retrieved successfully")
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting users: {e}")
            raise
    
    async def get_webinar_live_stream(self, webinar_id: str) -> Dict[str, Any]:
        """Get live stream details for a webinar"""
        try:
            headers = await self.auth.get_auth_headers()
            
            response = await self.http_client.get(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/livestream",
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get live stream: {response.status_code} - {response.text}")
            
            result = response.json()
            logger.info(f"Retrieved live stream for webinar: {webinar_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting live stream: {e}")
            raise
    
    async def get_webinar_invite_links(self, webinar_id: str) -> Dict[str, Any]:
        """Get invite links for a webinar"""
        try:
            headers = await self.auth.get_auth_headers()
            
            response = await self.http_client.get(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/invite_links",
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Failed to get invite links: {response.status_code} - {response.text}")
            
            result = response.json()
            logger.info(f"Retrieved invite links for webinar: {webinar_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting invite links: {e}")
            raise