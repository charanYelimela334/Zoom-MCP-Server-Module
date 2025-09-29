#!/usr/bin/env python3
"""
Zoom API DELETE Methods Module
Handles all DELETE operations for webinars
"""

import logging
from typing import Any, Dict

import httpx

from auth import ZoomAuth

logger = logging.getLogger("zoom-delete")


class ZoomDeleteMethods:
    """Handles all DELETE operations for Zoom webinars"""
    
    def __init__(self, auth: ZoomAuth):
        self.auth = auth
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
    
    async def delete_webinar(self, webinar_id: str, occurrence_id: str = None, cancel_webinar_reminder: bool = False) -> Dict[str, Any]:
        """
        Delete a webinar
        
        Args:
            webinar_id: The webinar ID
            occurrence_id: Webinar occurrence ID (for recurring webinars)
            cancel_webinar_reminder: Whether to send cancellation email to registrants
        """
        try:
            headers = await self.auth.get_auth_headers()
            
            # Build query parameters
            params = {}
            if occurrence_id:
                params["occurrence_id"] = occurrence_id
            if cancel_webinar_reminder:
                params["cancel_webinar_reminder"] = "true"
            
            response = await self.http_client.delete(
                f"{self.auth.config.base_url}/webinars/{webinar_id}",
                headers=headers,
                params=params
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to delete webinar: {response.status_code} - {response.text}")
            
            logger.info(f"Webinar deleted successfully: {webinar_id}")
            
            return {
                "success": True,
                "webinar_id": webinar_id,
                "message": "Webinar deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting webinar: {e}")
            raise
    
    async def remove_all_panelists(self, webinar_id: str) -> Dict[str, Any]:
        """Remove all panelists from a webinar"""
        try:
            headers = await self.auth.get_auth_headers()
            
            response = await self.http_client.delete(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/panelists",
                headers=headers
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to remove all panelists: {response.status_code} - {response.text}")
            
            logger.info(f"All panelists removed from webinar: {webinar_id}")
            
            return {
                "success": True,
                "webinar_id": webinar_id,
                "message": "All panelists removed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error removing all panelists: {e}")
            raise
    
    async def remove_panelist(self, webinar_id: str, panelist_id: str) -> Dict[str, Any]:
        """Remove a specific panelist from a webinar"""
        try:
            headers = await self.auth.get_auth_headers()
            
            response = await self.http_client.delete(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/panelists/{panelist_id}",
                headers=headers
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to remove panelist: {response.status_code} - {response.text}")
            
            logger.info(f"Panelist {panelist_id} removed from webinar: {webinar_id}")
            
            return {
                "success": True,
                "webinar_id": webinar_id,
                "panelist_id": panelist_id,
                "message": "Panelist removed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error removing panelist: {e}")
            raise
    
    async def delete_webinar_registrant(self, webinar_id: str, registrant_id: str, occurrence_id: str = None) -> Dict[str, Any]:
        """
        Delete a webinar registrant
        
        Args:
            webinar_id: The webinar ID
            registrant_id: The registrant ID
            occurrence_id: Webinar occurrence ID (for recurring webinars)
        """
        try:
            headers = await self.auth.get_auth_headers()
            
            # Build query parameters
            params = {}
            if occurrence_id:
                params["occurrence_id"] = occurrence_id
            
            response = await self.http_client.delete(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/registrants/{registrant_id}",
                headers=headers,
                params=params
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to delete registrant: {response.status_code} - {response.text}")
            
            logger.info(f"Registrant {registrant_id} deleted from webinar: {webinar_id}")
            
            return {
                "success": True,
                "webinar_id": webinar_id,
                "registrant_id": registrant_id,
                "message": "Registrant deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting registrant: {e}")
            raise
    
    async def delete_webinar_poll(self, webinar_id: str, poll_id: str) -> Dict[str, Any]:
        """Delete a webinar poll"""
        try:
            headers = await self.auth.get_auth_headers()
            
            response = await self.http_client.delete(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/polls/{poll_id}",
                headers=headers
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to delete poll: {response.status_code} - {response.text}")
            
            logger.info(f"Poll {poll_id} deleted from webinar: {webinar_id}")
            
            return {
                "success": True,
                "webinar_id": webinar_id,
                "poll_id": poll_id,
                "message": "Poll deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting poll: {e}")
            raise
    
    async def delete_webinar_tracking_source(self, webinar_id: str, source_id: str) -> Dict[str, Any]:
        """Delete a webinar tracking source"""
        try:
            headers = await self.auth.get_auth_headers()
            
            response = await self.http_client.delete(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/tracking_sources/{source_id}",
                headers=headers
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to delete tracking source: {response.status_code} - {response.text}")
            
            logger.info(f"Tracking source {source_id} deleted from webinar: {webinar_id}")
            
            return {
                "success": True,
                "webinar_id": webinar_id,
                "source_id": source_id,
                "message": "Tracking source deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting tracking source: {e}")
            raise
    
    async def delete_webinar_survey(self, webinar_id: str) -> Dict[str, Any]:
        """Delete a webinar survey"""
        try:
            headers = await self.auth.get_auth_headers()
            
            response = await self.http_client.delete(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/survey",
                headers=headers
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to delete survey: {response.status_code} - {response.text}")
            
            logger.info(f"Survey deleted from webinar: {webinar_id}")
            
            return {
                "success": True,
                "webinar_id": webinar_id,
                "message": "Survey deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting survey: {e}")
            raise
    
    async def delete_batch_registrants(self, webinar_id: str, registrant_ids: list, occurrence_id: str = None) -> Dict[str, Any]:
        """
        Delete multiple registrants in batch
        
        Args:
            webinar_id: The webinar ID
            registrant_ids: List of registrant IDs to delete
            occurrence_id: Webinar occurrence ID (for recurring webinars)
        """
        try:
            headers = await self.auth.get_auth_headers()
            
            # Build request data
            delete_data = {
                "registrants": [{"id": rid} for rid in registrant_ids]
            }
            
            # Build query parameters
            params = {}
            if occurrence_id:
                params["occurrence_id"] = occurrence_id
            
            response = await self.http_client.delete(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/registrants",
                headers=headers,
                json=delete_data,
                params=params
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to delete batch registrants: {response.status_code} - {response.text}")
            
            logger.info(f"Batch deleted {len(registrant_ids)} registrants from webinar: {webinar_id}")
            
            return {
                "success": True,
                "webinar_id": webinar_id,
                "deleted_count": len(registrant_ids),
                "message": f"Successfully deleted {len(registrant_ids)} registrants"
            }
            
        except Exception as e:
            logger.error(f"Error deleting batch registrants: {e}")
            raise