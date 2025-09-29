#!/usr/bin/env python3
"""
Zoom API PATCH Methods Module
Handles all PATCH operations for webinars (updates)
"""

import logging
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from auth import ZoomAuth

logger = logging.getLogger("zoom-patch")


class WebinarUpdateDetails(BaseModel):
    """Webinar update details"""
    topic: Optional[str] = None
    agenda: Optional[str] = None
    password: Optional[str] = None
    start_time: Optional[str] = None
    duration: Optional[int] = None
    timezone: Optional[str] = None
    host_video: Optional[bool] = None
    panelists_video: Optional[bool] = None
    practice_session: Optional[bool] = None
    hd_video: Optional[bool] = None
    approval_type: Optional[int] = None
    registration_type: Optional[int] = None
    audio: Optional[str] = None
    auto_recording: Optional[str] = None
    alternative_hosts: Optional[str] = None


class RegistrantStatusUpdate(BaseModel):
    """Registrant status update details"""
    action: str  # "approve", "cancel", "deny"
    registrants: List[Dict[str, str]]  # [{"id": "registrant_id", "email": "email"}]


class PanelistUpdate(BaseModel):
    """Panelist update details"""
    name: Optional[str] = None
    email: Optional[str] = None


class ZoomPatchMethods:
    """Handles all PATCH operations for Zoom webinars"""
    
    def __init__(self, auth: ZoomAuth):
        self.auth = auth
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
    
    async def update_webinar(self, webinar_id: str, update_details: WebinarUpdateDetails, occurrence_id: str = None) -> Dict[str, Any]:
        """
        Update a webinar
        
        Args:
            webinar_id: The webinar ID
            update_details: WebinarUpdateDetails with fields to update
            occurrence_id: Webinar occurrence ID (for recurring webinars)
        """
        try:
            headers = await self.auth.get_auth_headers()
            
            # Build update payload - only include non-None fields
            update_data = {}
            settings = {}
            
            # Basic webinar fields
            if update_details.topic is not None:
                update_data["topic"] = update_details.topic
            if update_details.agenda is not None:
                update_data["agenda"] = update_details.agenda
            if update_details.password is not None:
                update_data["password"] = update_details.password
            if update_details.start_time is not None:
                update_data["start_time"] = update_details.start_time
            if update_details.duration is not None:
                update_data["duration"] = update_details.duration
            if update_details.timezone is not None:
                update_data["timezone"] = update_details.timezone
            
            # Settings fields
            if update_details.host_video is not None:
                settings["host_video"] = update_details.host_video
            if update_details.panelists_video is not None:
                settings["panelists_video"] = update_details.panelists_video
            if update_details.practice_session is not None:
                settings["practice_session"] = update_details.practice_session
            if update_details.hd_video is not None:
                settings["hd_video"] = update_details.hd_video
            if update_details.approval_type is not None:
                settings["approval_type"] = update_details.approval_type
            if update_details.registration_type is not None:
                settings["registration_type"] = update_details.registration_type
            if update_details.audio is not None:
                settings["audio"] = update_details.audio
            if update_details.auto_recording is not None:
                settings["auto_recording"] = update_details.auto_recording
            if update_details.alternative_hosts is not None:
                settings["alternative_hosts"] = update_details.alternative_hosts
            
            if settings:
                update_data["settings"] = settings
            
            # Build query parameters
            params = {}
            if occurrence_id:
                params["occurrence_id"] = occurrence_id
            
            response = await self.http_client.patch(
                f"{self.auth.config.base_url}/webinars/{webinar_id}",
                headers=headers,
                json=update_data,
                params=params
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to update webinar: {response.status_code} - {response.text}")
            
            logger.info(f"Webinar updated successfully: {webinar_id}")
            
            # Return confirmation with updated fields
            return {
                "success": True,
                "webinar_id": webinar_id,
                "message": "Webinar updated successfully",
                "updated_fields": list(update_data.keys())
            }
            
        except Exception as e:
            logger.error(f"Error updating webinar: {e}")
            raise
    
    async def update_webinar_registrant_status(self, webinar_id: str, status_update: RegistrantStatusUpdate, occurrence_id: str = None) -> Dict[str, Any]:
        """
        Update webinar registrant status (approve, cancel, deny)
        
        Args:
            webinar_id: The webinar ID
            status_update: RegistrantStatusUpdate with action and registrant list
            occurrence_id: Webinar occurrence ID (for recurring webinars)
        """
        try:
            headers = await self.auth.get_auth_headers()
            
            update_data = {
                "action": status_update.action,
                "registrants": status_update.registrants
            }
            
            # Build query parameters
            params = {}
            if occurrence_id:
                params["occurrence_id"] = occurrence_id
            
            response = await self.http_client.patch(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/registrants/status",
                headers=headers,
                json=update_data,
                params=params
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to update registrant status: {response.status_code} - {response.text}")
            
            logger.info(f"Registrant status updated for webinar: {webinar_id}")
            
            return {
                "success": True,
                "webinar_id": webinar_id,
                "action": status_update.action,
                "affected_count": len(status_update.registrants),
                "message": f"Successfully {status_update.action}d {len(status_update.registrants)} registrants"
            }
            
        except Exception as e:
            logger.error(f"Error updating registrant status: {e}")
            raise
    
    async def update_webinar_status(self, webinar_id: str, action: str, occurrence_id: str = None) -> Dict[str, Any]:
        """
        Update webinar status (start, end, cancel)
        
        Args:
            webinar_id: The webinar ID
            action: Action to perform ("start", "end", "cancel")
            occurrence_id: Webinar occurrence ID (for recurring webinars)
        """
        try:
            headers = await self.auth.get_auth_headers()
            
            update_data = {
                "action": action
            }
            
            # Build query parameters
            params = {}
            if occurrence_id:
                params["occurrence_id"] = occurrence_id
            
            response = await self.http_client.patch(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/status",
                headers=headers,
                json=update_data,
                params=params
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to update webinar status: {response.status_code} - {response.text}")
            
            logger.info(f"Webinar status updated to '{action}' for webinar: {webinar_id}")
            
            return {
                "success": True,
                "webinar_id": webinar_id,
                "action": action,
                "message": f"Webinar {action} successfully"
            }
            
        except Exception as e:
            logger.error(f"Error updating webinar status: {e}")
            raise
    
    async def update_panelist(self, webinar_id: str, panelist_id: str, panelist_update: PanelistUpdate) -> Dict[str, Any]:
        """Update a webinar panelist"""
        try:
            headers = await self.auth.get_auth_headers()
            
            # Build update payload - only include non-None fields
            update_data = {}
            if panelist_update.name is not None:
                update_data["name"] = panelist_update.name
            if panelist_update.email is not None:
                update_data["email"] = panelist_update.email
            
            response = await self.http_client.patch(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/panelists/{panelist_id}",
                headers=headers,
                json=update_data
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to update panelist: {response.status_code} - {response.text}")
            
            logger.info(f"Panelist {panelist_id} updated for webinar: {webinar_id}")
            
            return {
                "success": True,
                "webinar_id": webinar_id,
                "panelist_id": panelist_id,
                "message": "Panelist updated successfully",
                "updated_fields": list(update_data.keys())
            }
            
        except Exception as e:
            logger.error(f"Error updating panelist: {e}")
            raise
    
    async def update_webinar_poll(self, webinar_id: str, poll_id: str, poll_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a webinar poll"""
        try:
            headers = await self.auth.get_auth_headers()
            
            response = await self.http_client.patch(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/polls/{poll_id}",
                headers=headers,
                json=poll_data
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to update poll: {response.status_code} - {response.text}")
            
            logger.info(f"Poll {poll_id} updated for webinar: {webinar_id}")
            
            return {
                "success": True,
                "webinar_id": webinar_id,
                "poll_id": poll_id,
                "message": "Poll updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error updating poll: {e}")
            raise
    
    async def update_live_stream(self, webinar_id: str, stream_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update webinar live stream settings"""
        try:
            headers = await self.auth.get_auth_headers()
            
            response = await self.http_client.patch(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/livestream",
                headers=headers,
                json=stream_data
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to update live stream: {response.status_code} - {response.text}")
            
            logger.info(f"Live stream updated for webinar: {webinar_id}")
            
            return {
                "success": True,
                "webinar_id": webinar_id,
                "message": "Live stream settings updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error updating live stream: {e}")
            raise
    
    async def update_webinar_survey(self, webinar_id: str, survey_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update webinar survey"""
        try:
            headers = await self.auth.get_auth_headers()
            
            response = await self.http_client.patch(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/survey",
                headers=headers,
                json=survey_data
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to update survey: {response.status_code} - {response.text}")
            
            logger.info(f"Survey updated for webinar: {webinar_id}")
            
            return {
                "success": True,
                "webinar_id": webinar_id,
                "message": "Survey updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error updating survey: {e}")
            raise
    
    async def update_webinar_branding(self, webinar_id: str, branding_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update webinar branding"""
        try:
            headers = await self.auth.get_auth_headers()
            
            response = await self.http_client.patch(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/branding",
                headers=headers,
                json=branding_data
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to update branding: {response.status_code} - {response.text}")
            
            logger.info(f"Branding updated for webinar: {webinar_id}")
            
            return {
                "success": True,
                "webinar_id": webinar_id,
                "message": "Branding updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error updating branding: {e}")
            raise
    
    async def update_registration_questions(self, webinar_id: str, questions_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update webinar registration questions"""
        try:
            headers = await self.auth.get_auth_headers()
            
            response = await self.http_client.patch(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/registrants/questions",
                headers=headers,
                json=questions_data
            )
            
            if response.status_code not in [200, 204]:
                raise Exception(f"Failed to update registration questions: {response.status_code} - {response.text}")
            
            logger.info(f"Registration questions updated for webinar: {webinar_id}")
            
            return {
                "success": True,
                "webinar_id": webinar_id,
                "message": "Registration questions updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error updating registration questions: {e}")
            raise