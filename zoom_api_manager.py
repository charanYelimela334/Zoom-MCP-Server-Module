#!/usr/bin/env python3
"""
Zoom API Manager - Main Module
Integrates all HTTP method modules and provides a unified interface
"""

import logging
import os
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from auth import ZoomAuth, ZoomConfig
from post_methods import (
    ZoomPostMethods, WebinarDetails, RecurringWebinarDetails,
    RecurrenceSettings, WebinarInviteLinks, PanelistDetails, WebinarPoll
)
from get_methods import ZoomGetMethods
from delete_methods import ZoomDeleteMethods
from patch_methods import (
    ZoomPatchMethods, WebinarUpdateDetails, RegistrantStatusUpdate, PanelistUpdate
)

logger = logging.getLogger("zoom-api-manager")


class ZoomAPIManager:
    """
    Unified Zoom API Manager
    Provides a single interface to all Zoom webinar operations
    """
    
    def __init__(self, config: ZoomConfig):
        self.config = config
        self.auth = ZoomAuth(config)
        self.post_methods = ZoomPostMethods(self.auth)
        self.get_methods = ZoomGetMethods(self.auth)
        self.delete_methods = ZoomDeleteMethods(self.auth)
        self.patch_methods = ZoomPatchMethods(self.auth)
    
    async def __aenter__(self):
        await self.auth.__aenter__()
        await self.post_methods.__aenter__()
        await self.get_methods.__aenter__()
        await self.delete_methods.__aenter__()
        await self.patch_methods.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.post_methods.__aexit__(exc_type, exc_val, exc_tb)
        await self.get_methods.__aexit__(exc_type, exc_val, exc_tb)
        await self.delete_methods.__aexit__(exc_type, exc_val, exc_tb)
        await self.patch_methods.__aexit__(exc_type, exc_val, exc_tb)
        await self.auth.__aexit__(exc_type, exc_val, exc_tb)
    
    # Authentication methods
    async def get_token_status(self) -> Dict[str, Any]:
        """Get current token status"""
        return self.auth.get_token_status()
    
    async def refresh_token(self) -> Dict[str, Any]:
        """Force refresh the access token"""
        return await self.auth.refresh_token()
    
    # User management
    async def get_users(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get users from Zoom account"""
        return await self.get_methods.get_users(user_id)
    
    async def get_user_by_selection(self, user_selection: str) -> Dict[str, Any]:
        """Get user by selection (number, name, or ID)"""
        try:
            users_data = await self.get_users()
            users = users_data.get('users', [])
            
            if not users:
                raise Exception("No users found in the account")
            
            # Clean up the selection input
            selection = user_selection.lower().strip()
            
            # Handle different selection formats
            if selection.startswith('user '):
                # "user 1", "user 2", etc.
                try:
                    user_num = int(selection.split()[1]) - 1  # Convert to 0-based index
                    if 0 <= user_num < len(users):
                        return users[user_num]
                    else:
                        raise Exception(f"User number {user_num + 1} not found. Available: 1-{len(users)}")
                except (ValueError, IndexError):
                    raise Exception("Invalid user selection format. Use 'user 1', 'user 2', etc.")
            
            elif selection.isdigit():
                # Just a number like "1", "2", etc.
                user_num = int(selection) - 1  # Convert to 0-based index
                if 0 <= user_num < len(users):
                    return users[user_num]
                else:
                    raise Exception(f"User number {int(selection)} not found. Available: 1-{len(users)}")
            
            elif selection in ['first', 'first user', '1st']:
                return users[0]
            
            elif selection in ['second', 'second user', '2nd']:
                if len(users) > 1:
                    return users[1]
                else:
                    raise Exception("Only 1 user available")
            
            elif selection in ['last', 'last user']:
                return users[-1]
            
            else:
                # Try to find by email or ID
                for user in users:
                    if (user.get('email', '').lower() == selection or 
                        user.get('id', '') == selection or
                        f"{user.get('first_name', '')} {user.get('last_name', '')}".lower().strip() == selection):
                        return user
                
                raise Exception(f"User '{user_selection}' not found. Please use user number (1, 2, etc.) or check available users.")
        
        except Exception as e:
            logger.error(f"Error selecting user: {e}")
            raise
    
    # POST Methods - Webinar Creation
    async def create_webinar(self, user_id: str, webinar_details: WebinarDetails) -> Dict[str, Any]:
        """Create a new webinar"""
        return await self.post_methods.create_webinar(user_id, webinar_details)
    
    async def create_recurring_webinar(self, user_id: str, webinar_details: RecurringWebinarDetails) -> Dict[str, Any]:
        """Create a recurring webinar"""
        return await self.post_methods.create_recurring_webinar(user_id, webinar_details)
    
    async def create_webinar_invite_links(self, webinar_id: str, invite_details: WebinarInviteLinks) -> Dict[str, Any]:
        """Create webinar invite links"""
        return await self.post_methods.create_webinar_invite_links(webinar_id, invite_details)
    
    async def add_panelists(self, webinar_id: str, panelists: List[PanelistDetails]) -> Dict[str, Any]:
        """Add panelists to a webinar"""
        return await self.post_methods.add_panelists(webinar_id, panelists)
    
    async def create_webinar_poll(self, webinar_id: str, poll: WebinarPoll) -> Dict[str, Any]:
        """Create a webinar poll"""
        return await self.post_methods.create_webinar_poll(webinar_id, poll)
    
    async def add_webinar_panelist(self, webinar_id: str, panelist: PanelistDetails) -> Dict[str, Any]:
        """Add a single panelist to a webinar"""
        return await self.post_methods.add_webinar_panelist(webinar_id, panelist)
    
    # GET Methods - Information Retrieval
    async def list_webinars(self, user_id: str, page_size: int = 30, page_number: int = 1) -> Dict[str, Any]:
        """List webinars for a user"""
        return await self.get_methods.list_webinars(user_id, page_size, page_number)
    
    async def get_webinar(self, webinar_id: str, occurrence_id: str = None, show_previous_occurrences: bool = False) -> Dict[str, Any]:
        """Get details of a specific webinar"""
        return await self.get_methods.get_webinar(webinar_id, occurrence_id, show_previous_occurrences)
    
    async def get_webinar_absentees(self, webinar_uuid: str, occurrence_id: str = None, page_size: int = 30, page_number: int = 1) -> Dict[str, Any]:
        """Get webinar absentees"""
        return await self.get_methods.get_webinar_absentees(webinar_uuid, occurrence_id, page_size, page_number)
    
    async def list_webinar_participants(self, webinar_uuid: str, occurrence_id: str = None, page_size: int = 30, page_number: int = 1) -> Dict[str, Any]:
        """List participants of a past webinar"""
        return await self.get_methods.list_webinar_participants(webinar_uuid, occurrence_id, page_size, page_number)
    
    async def list_webinar_qa(self, webinar_uuid: str, occurrence_id: str = None) -> Dict[str, Any]:
        """List Q&A of a past webinar"""
        return await self.get_methods.list_webinar_qa(webinar_uuid, occurrence_id)
    
    async def list_panelists(self, webinar_id: str) -> Dict[str, Any]:
        """List panelists of a webinar"""
        return await self.get_methods.list_panelists(webinar_id)
    
    async def get_webinar_registrant(self, webinar_id: str, registrant_id: str, occurrence_id: str = None) -> Dict[str, Any]:
        """Get a specific webinar registrant"""
        return await self.get_methods.get_webinar_registrant(webinar_id, registrant_id, occurrence_id)
    
    async def list_registration_questions(self, webinar_id: str) -> Dict[str, Any]:
        """List registration questions for a webinar"""
        return await self.get_methods.list_registration_questions(webinar_id)
    
    async def list_webinar_registrants(self, webinar_id: str, occurrence_id: str = None, status: str = "approved", page_size: int = 30, page_number: int = 1) -> Dict[str, Any]:
        """List webinar registrants"""
        return await self.get_methods.list_webinar_registrants(webinar_id, occurrence_id, status, page_size, page_number)
    
    async def get_webinar_polls(self, webinar_id: str) -> Dict[str, Any]:
        """Get polls for a webinar"""
        return await self.get_methods.get_webinar_polls(webinar_id)
    
    async def get_webinar_invite_links(self, webinar_id: str) -> Dict[str, Any]:
        """Get invite links for a webinar"""
        return await self.get_methods.get_webinar_invite_links(webinar_id)
    
    # DELETE Methods - Removal Operations
    async def delete_webinar(self, webinar_id: str, occurrence_id: str = None, cancel_webinar_reminder: bool = False) -> Dict[str, Any]:
        """Delete a webinar"""
        return await self.delete_methods.delete_webinar(webinar_id, occurrence_id, cancel_webinar_reminder)
    
    async def remove_all_panelists(self, webinar_id: str) -> Dict[str, Any]:
        """Remove all panelists from a webinar"""
        return await self.delete_methods.remove_all_panelists(webinar_id)
    
    async def remove_panelist(self, webinar_id: str, panelist_id: str) -> Dict[str, Any]:
        """Remove a specific panelist from a webinar"""
        return await self.delete_methods.remove_panelist(webinar_id, panelist_id)
    
    async def delete_webinar_registrant(self, webinar_id: str, registrant_id: str, occurrence_id: str = None) -> Dict[str, Any]:
        """Delete a webinar registrant"""
        return await self.delete_methods.delete_webinar_registrant(webinar_id, registrant_id, occurrence_id)
    
    # PATCH Methods - Update Operations
    async def update_webinar(self, webinar_id: str, update_details: WebinarUpdateDetails, occurrence_id: str = None) -> Dict[str, Any]:
        """Update a webinar"""
        return await self.patch_methods.update_webinar(webinar_id, update_details, occurrence_id)
    
    async def update_webinar_registrant_status(self, webinar_id: str, status_update: RegistrantStatusUpdate, occurrence_id: str = None) -> Dict[str, Any]:
        """Update webinar registrant status"""
        return await self.patch_methods.update_webinar_registrant_status(webinar_id, status_update, occurrence_id)
    
    async def update_webinar_status(self, webinar_id: str, action: str, occurrence_id: str = None) -> Dict[str, Any]:
        """Update webinar status (start, end, cancel)"""
        return await self.patch_methods.update_webinar_status(webinar_id, action, occurrence_id)
    
    # Helper Methods - Natural Language Processing
    def parse_prompt(self, prompt: str) -> WebinarDetails:
        """Parse natural language prompt to extract webinar details"""
        # Default values
        details = WebinarDetails(
            topic="Scheduled Webinar",
            duration=60,
            timezone="UTC"
        )
        
        # Extract topic
        topic_patterns = [
            r"(?:topic|title|subject):\s*([^,\n]+)",
            r"(?:about|regarding)\s+([^,\n]+)",
            r"webinar\s+(?:on|about)\s+([^,\n]+)",
            r"create\s+(?:a\s+)?webinar\s+about\s+([^,\n]+)",
            r"schedule\s+(?:a\s+)?webinar\s+about\s+([^,\n]+)"
        ]
        
        for pattern in topic_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                details.topic = match.group(1).strip().strip('"').strip("'")
                break
        
        # If no topic found in patterns, try to extract the main subject
        if details.topic == "Scheduled Webinar":
            # Look for common webinar topics
            words = prompt.lower().split()
            topic_indicators = ['about', 'on', 'regarding', 'covering', 'discussing']
            for i, word in enumerate(words):
                if word in topic_indicators and i + 1 < len(words):
                    # Take next few words as topic
                    topic_words = []
                    for j in range(i + 1, min(i + 5, len(words))):
                        if words[j] in [',', 'for', 'duration', 'minutes', 'hours']:
                            break
                        topic_words.append(words[j])
                    if topic_words:
                        details.topic = ' '.join(topic_words).title()
                        break
        
        # Extract duration
        duration_match = re.search(r"(?:duration|length|for)\s*:?\s*(\d+)\s*(?:minutes?|mins?|hours?|hrs?)", prompt, re.IGNORECASE)
        if duration_match:
            duration_val = int(duration_match.group(1))
            unit = duration_match.group(0).lower()
            if "hour" in unit or "hr" in unit:
                details.duration = duration_val * 60
            else:
                details.duration = duration_val
        
        # Extract start time
        time_patterns = [
            r"(?:start|time|at)\s*:?\s*([^,\n]+)",
            r"(?:on|date)\s*:?\s*([^,\n]+)"
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, prompt, re.IGNORECASE)
            if match:
                try:
                    time_str = match.group(1).strip()
                    # Try to parse the datetime
                    parsed_time = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                    details.start_time = parsed_time.isoformat() + "Z"
                except:
                    # If parsing fails, set to 1 hour from now
                    details.start_time = (datetime.now() + timedelta(hours=1)).isoformat() + "Z"
                break
        
        if not details.start_time:
            details.start_time = (datetime.now() + timedelta(hours=1)).isoformat() + "Z"
        
        return details
    
    def parse_recurring_prompt(self, prompt: str) -> RecurringWebinarDetails:
        """Parse natural language prompt to extract recurring webinar details"""
        # Start with base webinar details
        base_details = self.parse_prompt(prompt)
        
        # Default recurrence settings
        recurrence = RecurrenceSettings(
            type=2,  # Default to weekly
            repeat_interval=1,
            weekly_days="2",  # Default to Monday
            end_times=10
        )
        
        # Parse recurrence patterns
        prompt_lower = prompt.lower()
        
        # Daily patterns
        if any(word in prompt_lower for word in ["daily", "every day", "each day"]):
            recurrence.type = 1
            
            # Check for interval (every 2 days, etc.)
            interval_match = re.search(r"every\s+(\d+)\s+days?", prompt_lower)
            if interval_match:
                recurrence.repeat_interval = int(interval_match.group(1))
        
        # Weekly patterns
        elif any(word in prompt_lower for word in ["weekly", "every week", "each week"]):
            recurrence.type = 2
            
            # Parse specific days
            day_patterns = {
                "monday": "2", "mon": "2",
                "tuesday": "3", "tue": "3", "tues": "3",
                "wednesday": "4", "wed": "4",
                "thursday": "5", "thu": "5", "thur": "5", "thurs": "5",
                "friday": "6", "fri": "6",
                "saturday": "7", "sat": "7",
                "sunday": "1", "sun": "1"
            }
            
            selected_days = []
            for day_name, day_num in day_patterns.items():
                if day_name in prompt_lower:
                    selected_days.append(day_num)
            
            if selected_days:
                recurrence.weekly_days = ",".join(selected_days)
            
            # Check for interval (every 2 weeks, etc.)
            interval_match = re.search(r"every\s+(\d+)\s+weeks?", prompt_lower)
            if interval_match:
                recurrence.repeat_interval = int(interval_match.group(1))
        
        # Monthly patterns
        elif any(word in prompt_lower for word in ["monthly", "every month", "each month"]):
            recurrence.type = 3
            
            # Parse specific day of month
            day_match = re.search(r"(\d{1,2})(?:st|nd|rd|th)?\s+of\s+(?:each|every)\s+month", prompt_lower)
            if day_match:
                recurrence.monthly_day = int(day_match.group(1))
            else:
                # Default to same day of month as start date
                try:
                    start_dt = datetime.fromisoformat(base_details.start_time.replace('Z', '+00:00'))
                    recurrence.monthly_day = start_dt.day
                except:
                    recurrence.monthly_day = 1
        
        # Parse end conditions
        if "until" in prompt_lower or "end date" in prompt_lower or "end on" in prompt_lower:
            # Try to extract end date
            date_patterns = [
                r"until\s+([^\s,]+(?:\s+[^\s,]+)*)",
                r"end\s+(?:date|on)\s+([^\s,]+(?:\s+[^\s,]+)*)"
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, prompt_lower)
                if match:
                    try:
                        date_str = match.group(1).strip()
                        # Try to parse the date
                        end_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        recurrence.end_date_time = end_date.isoformat() + "Z"
                        recurrence.end_times = None
                        break
                    except:
                        continue
        
        # Parse number of occurrences
        occurrence_patterns = [
            r"(\d+)\s+(?:times?|occurrences?|sessions?|meetings?)",
            r"for\s+(\d+)\s+(?:weeks?|months?|days?)",
            r"repeat\s+(\d+)\s+times?"
        ]
        
        for pattern in occurrence_patterns:
            match = re.search(pattern, prompt_lower)
            if match and not recurrence.end_date_time:
                recurrence.end_times = int(match.group(1))
                break
        
        # Parse passcode/password
        password_match = re.search(r"(?:passcode|password):\s*([^\s,\n]+)", prompt, re.IGNORECASE)
        if password_match:
            base_details.password = password_match.group(1).strip()
        
        # Parse alternative hosts
        alt_hosts_match = re.search(r"(?:alternative\s+hosts?|alt\s+hosts?):\s*([^\n]+)", prompt, re.IGNORECASE)
        if alt_hosts_match:
            alt_hosts = alt_hosts_match.group(1).strip()
            # Clean up email list
            alt_hosts = re.sub(r'\s*,\s*', ',', alt_hosts)
        else:
            alt_hosts = ""
        
        return RecurringWebinarDetails(
            topic=base_details.topic,
            start_time=base_details.start_time,
            duration=base_details.duration,
            timezone="Asia/Kolkata",  # Default to IST
            agenda=base_details.agenda,
            password=base_details.password,
            host_video=base_details.host_video,
            panelists_video=base_details.panelists_video,
            practice_session=base_details.practice_session,
            hd_video=base_details.hd_video,
            approval_type=base_details.approval_type,
            registration_type=base_details.registration_type,
            audio=base_details.audio,
            auto_recording=base_details.auto_recording,
            alternative_hosts=alt_hosts,
            recurrence=recurrence
        )


def load_config_from_env() -> Optional[ZoomConfig]:
    """Load Zoom configuration from environment variables"""
    account_id = os.getenv('ZOOM_ACCOUNT_ID')
    client_id = os.getenv('ZOOM_CLIENT_ID')
    client_secret = os.getenv('ZOOM_CLIENT_SECRET')
    
    if account_id and client_id and client_secret:
        return ZoomConfig(
            account_id=account_id,
            client_id=client_id,
            client_secret=client_secret
        )
    return None