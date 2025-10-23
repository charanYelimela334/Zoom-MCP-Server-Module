#!/usr/bin/env python3
"""
Zoom API POST Methods Module
Handles all POST operations for webinars
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

from auth import ZoomAuth

logger = logging.getLogger("zoom-post")

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))


def convert_to_utc_iso(dt_str: str, from_tz: timezone = IST) -> str:
    """
    Convert a datetime string in the specified timezone to UTC ISO format.
    
    Args:
        dt_str: ISO format datetime string (with or without timezone info)
        from_tz: Timezone to assume if not in the string (default: IST)
    
    Returns:
        ISO format string with Z suffix (UTC)
    """
    try:
        # Try parsing with timezone info
        if 'Z' in dt_str or '+' in dt_str or dt_str.count('-') > 2:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        else:
            # Parse as naive datetime and assume the from_tz
            dt = datetime.fromisoformat(dt_str)
            dt = dt.replace(tzinfo=from_tz)
        
        # Convert to UTC
        dt_utc = dt.astimezone(timezone.utc)
        return dt_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
    except Exception as e:
        logger.warning(f"Failed to convert timezone for '{dt_str}': {e}")
        return dt_str


class WebinarDetails(BaseModel):
    """Webinar creation details"""
    topic: str
    start_time: Optional[str] = None
    duration: int = 60
    timezone: str = "Asia/Kolkata"  # Changed default to IST
    agenda: str = ""
    password: str = ""
    host_video: bool = True
    panelists_video: bool = False
    practice_session: bool = False
    hd_video: bool = False
    approval_type: int = 2  # 0=auto, 1=manual, 2=no registration
    registration_type: int = 1
    audio: str = "both"
    auto_recording: str = "none"
    alternative_hosts: str = ""


class RecurrenceSettings(BaseModel):
    """Recurrence settings for recurring webinars"""
    type: int  # 1=Daily, 2=Weekly, 3=Monthly
    repeat_interval: int = 1
    weekly_days: Optional[str] = None
    monthly_day: Optional[int] = None
    monthly_week: Optional[int] = None
    monthly_week_day: Optional[int] = None
    end_times: Optional[int] = None
    end_date_time: Optional[str] = None


class RecurringWebinarDetails(BaseModel):
    """Recurring webinar creation details"""
    topic: str
    start_time: str
    duration: int = 60
    timezone: str = "Asia/Kolkata"
    agenda: str = ""
    password: str = ""
    host_video: bool = True
    panelists_video: bool = False
    practice_session: bool = False
    hd_video: bool = False
    approval_type: int = 2
    registration_type: int = 1
    audio: str = "both"
    auto_recording: str = "none"
    alternative_hosts: str = ""
    recurrence: RecurrenceSettings


class WebinarInviteLinks(BaseModel):
    """Webinar invite links details"""
    ttl: int = 7200  # Time to live in seconds (2 hours default)
    

class PanelistDetails(BaseModel):
    """Panelist details for webinar"""
    email: str
    name: Optional[str] = None


class WebinarPoll(BaseModel):
    """Webinar poll details"""
    title: str
    questions: List[Dict[str, Any]]
    anonymous: bool = False


class ZoomPostMethods:
    """Handles all POST operations for Zoom webinars"""
    
    def __init__(self, auth: ZoomAuth):
        self.auth = auth
        self.http_client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.http_client.aclose()
    
    async def create_webinar(self, user_id: str, webinar_details: WebinarDetails) -> Dict[str, Any]:
        """Create a new webinar"""
        try:
            headers = await self.auth.get_auth_headers()
            
            # Set default start time if not provided (1 hour from now in IST, converted to UTC)
            if not webinar_details.start_time:
                now_ist = datetime.now(IST)
                future_ist = now_ist + timedelta(hours=1)
                webinar_details.start_time = future_ist.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            else:
                # Convert provided time to UTC if it's not already
                webinar_details.start_time = convert_to_utc_iso(webinar_details.start_time)
            
            webinar_data = {
                "topic": webinar_details.topic,
                "type": 5,  # Scheduled webinar
                "start_time": webinar_details.start_time,
                "duration": webinar_details.duration,
                "timezone": webinar_details.timezone,  # This tells Zoom to display times in this TZ
                "agenda": webinar_details.agenda,
                "password": webinar_details.password,
                "settings": {
                    "host_video": webinar_details.host_video,
                    "panelists_video": webinar_details.panelists_video,
                    "practice_session": webinar_details.practice_session,
                    "hd_video": webinar_details.hd_video,
                    "approval_type": webinar_details.approval_type,
                    "registration_type": webinar_details.registration_type,
                    "audio": webinar_details.audio,
                    "auto_recording": webinar_details.auto_recording,
                    "alternative_hosts": webinar_details.alternative_hosts
                }
            }
            
            response = await self.http_client.post(
                f"{self.auth.config.base_url}/users/{user_id}/webinars",
                headers=headers,
                json=webinar_data
            )
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to create webinar: {response.status_code} - {response.text}")
            
            webinar = response.json()
            logger.info(f"Webinar created successfully: {webinar.get('id')}")
            
            return {
                "id": webinar.get("id"),
                "uuid": webinar.get("uuid"),
                "topic": webinar.get("topic"),
                "start_time": webinar.get("start_time"),
                "duration": webinar.get("duration"),
                "timezone": webinar.get("timezone"),
                "join_url": webinar.get("join_url"),
                "start_url": webinar.get("start_url"),
                "registration_url": webinar.get("registration_url")
            }
            
        except Exception as e:
            logger.error(f"Error creating webinar: {e}")
            raise
    
    async def create_recurring_webinar(self, user_id: str, webinar_details: RecurringWebinarDetails) -> Dict[str, Any]:
        """Create a new recurring webinar"""
        try:
            headers = await self.auth.get_auth_headers()
            
            # Convert start_time to UTC if needed
            start_time_utc = convert_to_utc_iso(webinar_details.start_time)
            
            webinar_data = {
                "topic": webinar_details.topic,
                "type": 9,  # Recurring webinar with fixed time
                "start_time": start_time_utc,
                "duration": webinar_details.duration,
                "timezone": webinar_details.timezone,
                "agenda": webinar_details.agenda,
                "password": webinar_details.password,
                "recurrence": {
                    "type": webinar_details.recurrence.type,
                    "repeat_interval": webinar_details.recurrence.repeat_interval
                },
                "settings": {
                    "host_video": webinar_details.host_video,
                    "panelists_video": webinar_details.panelists_video,
                    "practice_session": webinar_details.practice_session,
                    "hd_video": webinar_details.hd_video,
                    "approval_type": webinar_details.approval_type,
                    "registration_type": webinar_details.registration_type,
                    "audio": webinar_details.audio,
                    "auto_recording": webinar_details.auto_recording,
                    "alternative_hosts": webinar_details.alternative_hosts
                }
            }
            
            # Add recurrence-specific settings
            recurrence = webinar_data["recurrence"]
            
            if webinar_details.recurrence.weekly_days:
                recurrence["weekly_days"] = webinar_details.recurrence.weekly_days
            
            if webinar_details.recurrence.monthly_day:
                recurrence["monthly_day"] = webinar_details.recurrence.monthly_day
                
            if webinar_details.recurrence.monthly_week and webinar_details.recurrence.monthly_week_day:
                recurrence["monthly_week"] = webinar_details.recurrence.monthly_week
                recurrence["monthly_week_day"] = webinar_details.recurrence.monthly_week_day
            
            if webinar_details.recurrence.end_times:
                recurrence["end_times"] = webinar_details.recurrence.end_times
            elif webinar_details.recurrence.end_date_time:
                # Convert end_date_time to UTC as well
                recurrence["end_date_time"] = convert_to_utc_iso(webinar_details.recurrence.end_date_time)
            else:
                # Default to 10 occurrences if no end condition specified
                recurrence["end_times"] = 10
            
            response = await self.http_client.post(
                f"{self.auth.config.base_url}/users/{user_id}/webinars",
                headers=headers,
                json=webinar_data
            )
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to create recurring webinar: {response.status_code} - {response.text}")
            
            webinar = response.json()
            logger.info(f"Recurring webinar created successfully: {webinar.get('id')}")
            
            return {
                "id": webinar.get("id"),
                "uuid": webinar.get("uuid"),
                "topic": webinar.get("topic"),
                "type": webinar.get("type"),
                "start_time": webinar.get("start_time"),
                "duration": webinar.get("duration"),
                "timezone": webinar.get("timezone"),
                "join_url": webinar.get("join_url"),
                "start_url": webinar.get("start_url"),
                "registration_url": webinar.get("registration_url"),
                "recurrence": webinar.get("recurrence"),
                "occurrences": webinar.get("occurrences", [])
            }
            
        except Exception as e:
            logger.error(f"Error creating recurring webinar: {e}")
            raise
    
    async def create_webinar_invite_links(self, webinar_id: str, invite_details: WebinarInviteLinks) -> Dict[str, Any]:
        """Create webinar invite links"""
        try:
            headers = await self.auth.get_auth_headers()
            
            invite_data = {
                "ttl": invite_details.ttl
            }
            
            response = await self.http_client.post(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/invite_links",
                headers=headers,
                json=invite_data
            )
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to create invite links: {response.status_code} - {response.text}")
            
            result = response.json()
            logger.info(f"Invite links created for webinar: {webinar_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating invite links: {e}")
            raise
    
    async def add_panelists(self, webinar_id: str, panelists: List[PanelistDetails]) -> Dict[str, Any]:
        """Add panelists to a webinar"""
        try:
            headers = await self.auth.get_auth_headers()
            
            panelist_data = {
                "panelists": [
                    {
                        "email": panelist.email,
                        "name": panelist.name or panelist.email.split('@')[0]
                    }
                    for panelist in panelists
                ]
            }
            
            response = await self.http_client.post(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/panelists",
                headers=headers,
                json=panelist_data
            )
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to add panelists: {response.status_code} - {response.text}")
            
            result = response.json()
            logger.info(f"Panelists added to webinar: {webinar_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error adding panelists: {e}")
            raise
    
    async def create_webinar_poll(self, webinar_id: str, poll: WebinarPoll) -> Dict[str, Any]:
        """Create a webinar poll"""
        try:
            headers = await self.auth.get_auth_headers()
            
            poll_data = {
                "title": poll.title,
                "questions": poll.questions,
                "anonymous": poll.anonymous
            }
            
            response = await self.http_client.post(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/polls",
                headers=headers,
                json=poll_data
            )
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to create poll: {response.status_code} - {response.text}")
            
            result = response.json()
            logger.info(f"Poll created for webinar: {webinar_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error creating poll: {e}")
            raise
    
    async def add_webinar_panelist(self, webinar_id: str, panelist: PanelistDetails) -> Dict[str, Any]:
        """Add a single panelist to a webinar"""
        try:
            headers = await self.auth.get_auth_headers()
            
            panelist_data = {
                "email": panelist.email,
                "name": panelist.name or panelist.email.split('@')[0]
            }
            
            response = await self.http_client.post(
                f"{self.auth.config.base_url}/webinars/{webinar_id}/panelists",
                headers=headers,
                json=panelist_data
            )
            
            if response.status_code not in [200, 201]:
                raise Exception(f"Failed to add panelist: {response.status_code} - {response.text}")
            
            result = response.json()
            logger.info(f"Panelist {panelist.email} added to webinar: {webinar_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error adding panelist: {e}")
            raise