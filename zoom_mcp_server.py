"""
Zoom Webinar MCP Server - Modular Architecture
Complete server implementation using modular HTTP method architecture
Version: 3.0.1
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.lowlevel.server import NotificationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent

# Constants
SERVER_NAME = "zoom-webinar-mcp-server"
SERVER_VERSION = "3.0.1"
DEFAULT_PAGE_SIZE = 30
DEFAULT_DURATION = 60
DEFAULT_TIMEZONE = "UTC"

# Custom Exceptions
class ZoomMCPError(Exception):
    """Base exception for Zoom MCP server errors"""
    pass

class ConfigurationError(ZoomMCPError):
    """Raised when configuration is invalid or missing"""
    pass

class ModuleImportError(ZoomMCPError):
    """Raised when required modules cannot be imported"""
    pass

# Validate and import required modules
try:
    from auth import ZoomConfig
    from zoom_api_manager import ZoomAPIManager, load_config_from_env
    from post_methods import (
        WebinarDetails, 
        RecurringWebinarDetails, 
        RecurrenceSettings, 
        PanelistDetails, 
        WebinarPoll
    )
    from patch_methods import WebinarUpdateDetails, RegistrantStatusUpdate
    from get_methods import ZoomGetMethods
    from delete_methods import ZoomDeleteMethods
except ImportError as e:
    print(f"FATAL ERROR: Failed to import required modules: {e}", file=sys.stderr)
    print("Please ensure all module files are present:", file=sys.stderr)
    print("  - auth.py", file=sys.stderr)
    print("  - zoom_api_manager.py", file=sys.stderr)
    print("  - post_methods.py", file=sys.stderr)
    print("  - patch_methods.py", file=sys.stderr)
    print("  - get_methods.py", file=sys.stderr)
    print("  - delete_methods.py", file=sys.stderr)
    sys.exit(1)

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("WARNING: python-dotenv not installed. Install with: pip install python-dotenv", file=sys.stderr)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zoom_mcp_server.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("zoom-mcp-server")

# Initialize the MCP server
server = Server(SERVER_NAME)

# Global API manager instance with lock for thread safety
api_manager: Optional[ZoomAPIManager] = None
api_manager_lock = asyncio.Lock()


async def cleanup_api_manager() -> None:
    """Safely cleanup API manager"""
    global api_manager
    if api_manager:
        try:
            await api_manager.__aexit__(None, None, None)
            logger.info("API manager cleaned up successfully")
        except Exception as e:
            logger.error(f"Error during API manager cleanup: {e}", exc_info=True)
        finally:
            api_manager = None


async def initialize_api_manager(config: ZoomConfig) -> None:
    """Safely initialize API manager"""
    global api_manager
    async with api_manager_lock:
        await cleanup_api_manager()
        api_manager = ZoomAPIManager(config)
        await api_manager.__aenter__()
        logger.info("API manager initialized successfully")


def ensure_api_configured() -> bool:
    """Check if API manager is configured"""
    return api_manager is not None


def format_list_output(items: List[str]) -> str:
    """Format a list of items as a string"""
    return "\n".join(items)


@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="zoom://config",
            name="Zoom Configuration",
            description="Current Zoom API configuration status",
            mimeType="application/json"
        ),
        Resource(
            uri="zoom://token-status",
            name="Token Status", 
            description="Current access token status and expiry information",
            mimeType="application/json"
        ),
        Resource(
            uri="zoom://users",
            name="Account Users",
            description="List all users in the Zoom account",
            mimeType="application/json"
        ),
        Resource(
            uri="zoom://env-status",
            name="Environment Status",
            description="Check if environment variables are properly loaded",
            mimeType="application/json"
        )
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read resource content"""
    try:
        if uri == "zoom://config":
            if api_manager:
                return json.dumps({
                    "configured": True,
                    "account_id": api_manager.config.account_id[:8] + "...",
                    "base_url": api_manager.config.base_url,
                    "token_cache_active": api_manager.auth.token_cache.access_token is not None
                }, indent=2)
            return json.dumps({"configured": False}, indent=2)
        
        elif uri == "zoom://token-status":
            if not api_manager:
                return json.dumps({"error": "Zoom not configured"}, indent=2)
            status = await api_manager.get_token_status()
            return json.dumps(status, indent=2)
        
        elif uri == "zoom://users":
            if not api_manager:
                return json.dumps({"error": "Zoom not configured"}, indent=2)
            try:
                users_data = await api_manager.get_users()
                return json.dumps(users_data, indent=2)
            except Exception as e:
                logger.error(f"Failed to get users: {e}", exc_info=True)
                return json.dumps({"error": f"Failed to get users: {str(e)}"}, indent=2)
        
        elif uri == "zoom://env-status":
            env_config = load_config_from_env()
            if env_config:
                return json.dumps({
                    "status": "loaded",
                    "account_id": env_config.account_id[:8] + "..." if env_config.account_id else None,
                    "client_id": env_config.client_id[:8] + "..." if env_config.client_id else None,
                    "client_secret": "***loaded***" if env_config.client_secret else None
                }, indent=2)
            return json.dumps({
                "status": "missing",
                "message": "Environment variables not found. Check .env file.",
                "required": ["ZOOM_ACCOUNT_ID", "ZOOM_CLIENT_ID", "ZOOM_CLIENT_SECRET"]
            }, indent=2)
        
        raise ValueError(f"Unknown resource: {uri}")
    
    except Exception as e:
        logger.error(f"Error reading resource {uri}: {e}", exc_info=True)
        return json.dumps({"error": str(e)}, indent=2)


@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools"""
    tools = [
        # Configuration tools
        Tool(
            name="auto_configure_zoom",
            description="Auto-configure Zoom API from environment variables (.env file)",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="configure_zoom",
            description="Manually configure Zoom API credentials",
            inputSchema={
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "Zoom account ID"},
                    "client_id": {"type": "string", "description": "Zoom app client ID"},
                    "client_secret": {"type": "string", "description": "Zoom app client secret"}
                },
                "required": ["account_id", "client_id", "client_secret"]
            }
        ),
        
        # Authentication and status tools
        Tool(
            name="get_token_status",
            description="Check current access token status and remaining time",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="refresh_token",
            description="Force refresh the access token",
            inputSchema={"type": "object", "properties": {}}
        ),
        
        # User management tools
        Tool(
            name="list_users_for_selection",
            description="List all users with numbers for easy selection when creating webinars",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="get_users",
            description="Get Zoom account users",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Optional specific user ID"}
                }
            }
        ),
        
        # POST methods - Creation tools
        Tool(
            name="create_webinar",
            description="Create a new Zoom webinar",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID to create webinar for"},
                    "topic": {"type": "string", "description": "Webinar topic/title"},
                    "start_time": {"type": "string", "description": "Start time in ISO format (optional)"},
                    "duration": {"type": "integer", "description": "Duration in minutes", "default": DEFAULT_DURATION},
                    "agenda": {"type": "string", "description": "Webinar agenda"},
                    "timezone": {"type": "string", "description": "Timezone", "default": DEFAULT_TIMEZONE},
                    "password": {"type": "string", "description": "Webinar password"},
                    "alternative_hosts": {"type": "string", "description": "Alternative hosts emails"}
                },
                "required": ["user_id", "topic"]
            }
        ),
        Tool(
            name="create_webinar_interactive",
            description="Create webinar with interactive user selection",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Webinar topic/title"},
                    "user_selection": {"type": "string", "description": "User selection (e.g., 'user 1', '1', 'first user')"},
                    "start_time": {"type": "string", "description": "Start time in ISO format (optional)"},
                    "duration": {"type": "integer", "description": "Duration in minutes", "default": DEFAULT_DURATION},
                    "agenda": {"type": "string", "description": "Webinar agenda"},
                    "timezone": {"type": "string", "description": "Timezone", "default": DEFAULT_TIMEZONE}
                },
                "required": ["topic", "user_selection"]
            }
        ),
        Tool(
            name="create_recurring_webinar",
            description="Create a new recurring Zoom webinar",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID to create webinar for"},
                    "topic": {"type": "string", "description": "Webinar topic/title"},
                    "start_time": {"type": "string", "description": "Start time in ISO format (required)"},
                    "duration": {"type": "integer", "description": "Duration in minutes", "default": DEFAULT_DURATION},
                    "recurrence_type": {"type": "integer", "description": "1=Daily, 2=Weekly, 3=Monthly", "default": 2},
                    "repeat_interval": {"type": "integer", "description": "Repeat every X units", "default": 1},
                    "weekly_days": {"type": "string", "description": "For weekly: comma-separated days (1=Sun, 2=Mon, etc.)"},
                    "end_times": {"type": "integer", "description": "Number of occurrences"},
                    "password": {"type": "string", "description": "Webinar password"},
                    "alternative_hosts": {"type": "string", "description": "Alternative hosts emails"}
                },
                "required": ["user_id", "topic", "start_time"]
            }
        ),
        Tool(
            name="add_panelists",
            description="Add panelists to a webinar",
            inputSchema={
                "type": "object",
                "properties": {
                    "webinar_id": {"type": "string", "description": "Webinar ID"},
                    "panelist_emails": {"type": "array", "items": {"type": "string"}, "description": "List of panelist email addresses"}
                },
                "required": ["webinar_id", "panelist_emails"]
            }
        ),
        Tool(
            name="create_webinar_poll",
            description="Create a poll for a webinar",
            inputSchema={
                "type": "object",
                "properties": {
                    "webinar_id": {"type": "string", "description": "Webinar ID"},
                    "poll_title": {"type": "string", "description": "Poll title"},
                    "questions": {"type": "array", "description": "Poll questions"}
                },
                "required": ["webinar_id", "poll_title", "questions"]
            }
        ),
        
        # GET methods - Information retrieval tools
        Tool(
            name="list_webinars",
            description="List webinars for a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID"},
                    "page_size": {"type": "integer", "description": "Number of results per page", "default": DEFAULT_PAGE_SIZE},
                    "page_number": {"type": "integer", "description": "Page number", "default": 1},
                    "type": {
                        "type": "string", 
                        "description": "Type of webinars to retrieve: 'scheduled' (all valid previous, live, and upcoming) or 'upcoming' (upcoming and live only)", 
                        "default": "scheduled",
                        "enum": ["scheduled", "upcoming"]
                    }
                },
                "required": ["user_id"]
            }
    ),
        Tool(
            name="list_webinar_qa",
            description="Get Q&A questions and answers from a past webinar",
            inputSchema={
                "type": "object",
                "properties": {
                    "webinar_id": {"type": "string", "description": "Webinar ID"},
                    "occurrence_id": {"type": "string", "description": "Occurrence ID for recurring webinars"}
                },
                "required": ["webinar_id"]
            }
        ),
        Tool(
            name="get_webinar",
            description="Get details of a specific webinar",
            inputSchema={
                "type": "object",
                "properties": {
                    "webinar_id": {"type": "string", "description": "Webinar ID"},
                    "occurrence_id": {"type": "string", "description": "Occurrence ID for recurring webinars"},
                    "show_previous_occurrences": {"type": "boolean", "description": "Show previous occurrences", "default": False}
                },
                "required": ["webinar_id"]
            }
        ),
        Tool(
            name="list_webinar_participants",
            description="List participants of a past webinar",
            inputSchema={
                "type": "object",
                "properties": {
                    "webinar_uuid": {"type": "string", "description": "Webinar UUID"},
                    "occurrence_id": {"type": "string", "description": "Occurrence ID for recurring webinars"},
                    "page_size": {"type": "integer", "description": "Number of results per page", "default": DEFAULT_PAGE_SIZE}
                },
                "required": ["webinar_uuid"]
            }
        ),
        Tool(
            name="list_webinar_registrants", 
            description="List webinar registrants with their IDs for management",
            inputSchema={
                "type": "object",
                "properties": {
                    "webinar_id": {"type": "string", "description": "Webinar ID"},
                    "status": {"type": "string", "description": "Registrant status", "default": "approved"},
                    "page_size": {"type": "integer", "description": "Number of results per page", "default": DEFAULT_PAGE_SIZE}
                },
                "required": ["webinar_id"]
            }
        ),
        Tool(
            name="find_registrant_by_email",
            description="Find a registrant ID by their email address - useful before deleting",
            inputSchema={
                "type": "object",
                "properties": {
                    "webinar_id": {"type": "string", "description": "Webinar ID"},
                    "email": {"type": "string", "description": "Registrant email address"}
                },
                "required": ["webinar_id", "email"]
            }
        ),
        Tool(
            name="list_panelists",
            description="List panelists of a webinar",
            inputSchema={
                "type": "object",
                "properties": {
                    "webinar_id": {"type": "string", "description": "Webinar ID"}
                },
                "required": ["webinar_id"]
            }
        ),
        
        # DELETE methods - Removal tools
        Tool(
            name="delete_webinar",
            description="Delete a Zoom webinar",
            inputSchema={
                "type": "object",
                "properties": {
                    "webinar_id": {"type": "string", "description": "Webinar ID to delete"},
                    "occurrence_id": {"type": "string", "description": "Occurrence ID for recurring webinars"},
                    "cancel_webinar_reminder": {"type": "boolean", "description": "Send cancellation email", "default": False}
                },
                "required": ["webinar_id"]
            }
        ),
        Tool(
            name="remove_panelist",
            description="Remove a panelist from a webinar",
            inputSchema={
                "type": "object",
                "properties": {
                    "webinar_id": {"type": "string", "description": "Webinar ID"},
                    "panelist_id": {"type": "string", "description": "Panelist ID to remove"}
                },
                "required": ["webinar_id", "panelist_id"]
            }
        ),
        Tool(
            name="delete_webinar_registrant",
            description="Delete a webinar registrant - use list_webinar_registrants or find_registrant_by_email to get the registrant_id first",
            inputSchema={
                "type": "object",
                "properties": {
                    "webinar_id": {"type": "string", "description": "Webinar ID"},
                    "registrant_id": {"type": "string", "description": "Registrant ID to delete (get this from list_webinar_registrants)"}
                },
                "required": ["webinar_id", "registrant_id"]
            }
        ),
        
        # PATCH methods - Update tools
        Tool(
            name="update_webinar",
            description="Update a webinar",
            inputSchema={
                "type": "object", 
                "properties": {
                    "webinar_id": {"type": "string", "description": "Webinar ID"},
                    "topic": {"type": "string", "description": "New webinar topic"},
                    "start_time": {"type": "string", "description": "New start time in ISO format"},
                    "duration": {"type": "integer", "description": "New duration in minutes"},
                    "agenda": {"type": "string", "description": "New agenda"},
                    "password": {"type": "string", "description": "New password"}
                },
                "required": ["webinar_id"]
            }
        ),
        Tool(
            name="update_webinar_status",
            description="Update webinar status (start, end, cancel)",
            inputSchema={
                "type": "object",
                "properties": {
                    "webinar_id": {"type": "string", "description": "Webinar ID"},
                    "action": {"type": "string", "description": "Action: start, end, or cancel"},
                    "occurrence_id": {"type": "string", "description": "Occurrence ID for recurring webinars"}
                },
                "required": ["webinar_id", "action"]
            }
        ),
        
        # Natural language processing tools
        Tool(
            name="schedule_webinar_from_prompt",
            description="Schedule a webinar from natural language prompt",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Natural language description of the webinar"},
                    "user_selection": {"type": "string", "description": "User selection (e.g., 'user 1', '1', 'first user')"}
                },
                "required": ["prompt", "user_selection"]
            }
        ),
        Tool(
            name="schedule_recurring_webinar_from_prompt", 
            description="Schedule recurring webinar from natural language prompt",
            inputSchema={
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "Natural language description of the recurring webinar"},
                    "user_selection": {"type": "string", "description": "User selection (e.g., 'user 1', '1', 'first user')"}
                },
                "required": ["prompt", "user_selection"]
            }
        )
    ]
    
    return tools


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    global api_manager
    
    try:
        # Configuration tools
        if name == "auto_configure_zoom":
            env_config = load_config_from_env()
            
            if not env_config:
                return [TextContent(
                    type="text",
                    text="Environment variables not found!\n\n"
                         "Please create a .env file with:\n"
                         "ZOOM_ACCOUNT_ID=your_account_id\n"
                         "ZOOM_CLIENT_ID=your_client_id\n"
                         "ZOOM_CLIENT_SECRET=your_client_secret"
                )]
            
            await initialize_api_manager(env_config)
            
            return [TextContent(
                type="text",
                text=f"Zoom API auto-configured from environment!\n"
                     f"Account ID: {env_config.account_id[:8]}...\n"
                     f"Smart token caching is now active!"
            )]
        
        elif name == "configure_zoom":
            config = ZoomConfig(
                account_id=arguments["account_id"],
                client_id=arguments["client_id"],
                client_secret=arguments["client_secret"]
            )
            
            await initialize_api_manager(config)
            
            return [TextContent(
                type="text",
                text="Zoom API configured manually! Token caching is now active."
            )]
        
        # Check if API manager is configured
        if not ensure_api_configured():
            return [TextContent(
                type="text",
                text="Zoom API not configured. Please run 'auto_configure_zoom' or 'configure_zoom' first."
            )]
        
        # Authentication and status tools
        if name == "get_token_status":
            status = await api_manager.get_token_status()
            
            if status["status"] == "no_token":
                result = "No access token cached"
            elif status["status"] == "valid":
                result = f"Access token is VALID\nRemaining time: {status['remaining_minutes']} minutes"
            else:
                result = "Access token has EXPIRED\nWill generate new token on next request"
            
            return [TextContent(type="text", text=result)]
        
        elif name == "refresh_token":
            await api_manager.refresh_token()
            status = await api_manager.get_token_status()
            
            result = f"Token refreshed successfully!\nValid for: {status['remaining_minutes']} minutes"
            
            return [TextContent(type="text", text=result)]
        
        # User management tools
        elif name == "list_users_for_selection":
            users_data = await api_manager.get_users()
            users = users_data.get('users', [])
            
            if not users:
                return [TextContent(
                    type="text",
                    text="No users found in the account. Please add users first."
                )]
            
            lines = ["Available Users for Webinar Creation:", ""]
            for i, user in enumerate(users, 1):
                lines.append(f"{i}. {user.get('email')} (ID: {user.get('id')})")
                if user.get('first_name') or user.get('last_name'):
                    lines.append(f"   Name: {user.get('first_name', '')} {user.get('last_name', '')}")
                lines.append(f"   Type: {user.get('type')}")
                lines.append("")
            
            lines.append("To create a webinar, use: 'user 1', 'user 2', or just '1', '2', etc.")
            
            return [TextContent(type="text", text=format_list_output(lines))]
        
        elif name == "get_users":
            user_id = arguments.get("user_id")
            users_data = await api_manager.get_users(user_id)
            
            if not users_data:
                return [TextContent(type="text", text="No user data returned")]
            
            if user_id:
                lines = [
                    "User Details:",
                    f"ID: {users_data.get('id')}",
                    f"Email: {users_data.get('email')}",
                    f"First Name: {users_data.get('first_name')}",
                    f"Last Name: {users_data.get('last_name')}",
                    f"Type: {users_data.get('type')}"
                ]
            else:
                users = users_data.get('users', [])
                lines = [f"Found {len(users)} users:", ""]
                for user in users[:10]:
                    lines.append(f"• {user.get('email')} (ID: {user.get('id')})")
                if len(users) > 10:
                    lines.append(f"... and {len(users) - 10} more users")
            
            return [TextContent(type="text", text=format_list_output(lines))]
        
        # POST methods - Creation tools
        elif name == "create_webinar":
            webinar_details = WebinarDetails(
                topic=arguments["topic"],
                start_time=arguments.get("start_time"),
                duration=arguments.get("duration", DEFAULT_DURATION),
                agenda=arguments.get("agenda", ""),
                timezone=arguments.get("timezone", DEFAULT_TIMEZONE),
                password=arguments.get("password", ""),
                alternative_hosts=arguments.get("alternative_hosts", "")
            )
            
            webinar = await api_manager.create_webinar(arguments["user_id"], webinar_details)
            
            lines = [
                "Webinar Created Successfully!",
                "",
                f"ID: {webinar['id']}",
                f"Topic: {webinar['topic']}",
                f"Start Time: {webinar['start_time']}",
                f"Duration: {webinar['duration']} minutes",
                f"Join URL: {webinar['join_url']}",
                f"Start URL: {webinar['start_url']}"
            ]
            
            if webinar.get('registration_url'):
                lines.append(f"Registration URL: {webinar['registration_url']}")
            
            return [TextContent(type="text", text=format_list_output(lines))]
        
        elif name == "create_webinar_interactive":
            try:
                selected_user = await api_manager.get_user_by_selection(arguments["user_selection"])
            except Exception as e:
                return [TextContent(
                    type="text",
                    text=f"User selection error: {str(e)}\n\nUse 'list_users_for_selection' to see available users."
                )]
            
            webinar_details = WebinarDetails(
                topic=arguments["topic"],
                start_time=arguments.get("start_time"),
                duration=arguments.get("duration", DEFAULT_DURATION),
                agenda=arguments.get("agenda", ""),
                timezone=arguments.get("timezone", DEFAULT_TIMEZONE)
            )
            
            webinar = await api_manager.create_webinar(selected_user['id'], webinar_details)
            
            lines = [
                "Webinar Created Successfully!",
                f"User: {selected_user.get('email')} ({selected_user.get('id')})",
                "",
                f"ID: {webinar['id']}",
                f"Topic: {webinar['topic']}",
                f"Start Time: {webinar['start_time']}",
                f"Duration: {webinar['duration']} minutes",
                f"Join URL: {webinar['join_url']}",
                f"Start URL: {webinar['start_url']}"
            ]
            
            return [TextContent(type="text", text=format_list_output(lines))]
        
        elif name == "create_recurring_webinar":
            recurrence = RecurrenceSettings(
                type=arguments.get("recurrence_type", 2),
                repeat_interval=arguments.get("repeat_interval", 1),
                weekly_days=arguments.get("weekly_days"),
                end_times=arguments.get("end_times")
            )
            
            webinar_details = RecurringWebinarDetails(
                topic=arguments["topic"],
                start_time=arguments["start_time"],
                duration=arguments.get("duration", DEFAULT_DURATION),
                password=arguments.get("password", ""),
                alternative_hosts=arguments.get("alternative_hosts", ""),
                recurrence=recurrence
            )
            
            webinar = await api_manager.create_recurring_webinar(arguments["user_id"], webinar_details)
            
            lines = [
                "Recurring Webinar Created Successfully!",
                "",
                f"ID: {webinar['id']}",
                f"Topic: {webinar['topic']}",
                f"Start Time: {webinar['start_time']}",
                f"Duration: {webinar['duration']} minutes",
                f"Total Occurrences: {len(webinar.get('occurrences', []))}",
                f"Join URL: {webinar['join_url']}"
            ]
            
            return [TextContent(type="text", text=format_list_output(lines))]
        
        elif name == "add_panelists":
            panelists = [PanelistDetails(email=email) for email in arguments["panelist_emails"]]
            await api_manager.add_panelists(arguments["webinar_id"], panelists)
            
            return [TextContent(
                type="text",
                text=f"Successfully added {len(panelists)} panelists to webinar {arguments['webinar_id']}"
            )]
        
        elif name == "create_webinar_poll":
            poll = WebinarPoll(
                title=arguments["poll_title"],
                questions=arguments["questions"]
            )
            await api_manager.create_webinar_poll(arguments["webinar_id"], poll)
            
            return [TextContent(
                type="text",
                text=f"Poll '{arguments['poll_title']}' created successfully for webinar {arguments['webinar_id']}"
            )]
        
        # GET methods - Information retrieval tools
        elif name == "list_webinar_qa":
            qa_data = await api_manager.list_webinar_qa(
                arguments["webinar_id"],
                arguments.get("occurrence_id")
            )
            participants = qa_data.get("questions", [])
        
            if not participants:
                result = f"No Q&A data found for webinar {arguments['webinar_id']}"
            else:
                total_questions = sum(len(p.get('question_details', [])) for p in participants)
                lines = [f"Found {total_questions} Q&A items from {len(participants)} participant(s):", ""]
            
                q_number = 1
                for participant in participants:
                    participant_name = participant.get('name') or "Anonymous"
                    participant_email = participant.get('email') or "N/A"
                
                    for detail in participant.get('question_details', []):
                        question_text = detail.get('question') or "[Question text not available]"
                        answer_text = detail.get('answer') if detail.get('answer') else "Not answered"
                    
                        lines.extend([
                            f"Q{q_number}: {question_text}",
                            f"   Asked by: {participant_name} ({participant_email})",
                            f"   Answer: {answer_text}",
                            ""
                        ])
                        q_number += 1
                
                result = format_list_output(lines)
        
            return [TextContent(type="text", text=result)]

        elif name == "list_webinars":
            webinars = await api_manager.list_webinars(
                arguments["user_id"],
                arguments.get("page_size", DEFAULT_PAGE_SIZE),
                arguments.get("page_number", 1),
                arguments.get("type", "scheduled")
            )
            
            webinar_list = webinars.get("webinars", [])
            webinar_type = arguments.get("type", "scheduled")
            
            if not webinar_list:
                result = f"No {webinar_type} webinars found for user {arguments['user_id']}"
            else:
                lines = [f"Found {len(webinar_list)} {webinar_type} webinars:", ""]
                for webinar in webinar_list:
                    lines.extend([
                        f"• {webinar.get('topic')} (ID: {webinar.get('id')})",
                        f"  Start: {webinar.get('start_time')}",
                        f"  Duration: {webinar.get('duration')} minutes",
                        ""
                    ])
                
                result = format_list_output(lines)
            
            return [TextContent(type="text", text=result)]
        
        elif name == "get_webinar":
            webinar = await api_manager.get_webinar(
                arguments["webinar_id"],
                arguments.get("occurrence_id"),
                arguments.get("show_previous_occurrences", False)
            )
            
            lines = [
                "Webinar Details:",
                "",
                f"ID: {webinar.get('id')}",
                f"Topic: {webinar.get('topic')}",
                f"Start Time: {webinar.get('start_time')}",
                f"Duration: {webinar.get('duration')} minutes",
                f"Status: {webinar.get('status')}",
                f"Join URL: {webinar.get('join_url')}"
            ]
            
            return [TextContent(type="text", text=format_list_output(lines))]
        
        elif name == "list_webinar_participants":
            participants = await api_manager.list_webinar_participants(
                arguments["webinar_uuid"],
                arguments.get("occurrence_id"),
                arguments.get("page_size", DEFAULT_PAGE_SIZE)
            )
            
            participant_list = participants.get("participants", [])
            lines = [f"Found {len(participant_list)} participants:", ""]
            
            for participant in participant_list[:10]:
                lines.extend([
                    f"• {participant.get('name')} ({participant.get('email')})",
                    f"  Join Time: {participant.get('join_time')}",
                    f"  Duration: {participant.get('duration')} minutes",
                    ""
                ])
            
            if len(participant_list) > 10:
                lines.append(f"... and {len(participant_list) - 10} more participants")
            
            return [TextContent(type="text", text=format_list_output(lines))]
        
        elif name == "list_webinar_registrants":
            registrants = await api_manager.list_webinar_registrants(
                arguments["webinar_id"],
                status=arguments.get("status", "approved"),
                page_size=arguments.get("page_size", DEFAULT_PAGE_SIZE)
            )
            
            registrant_list = registrants.get("registrants", [])
            lines = [f"Found {len(registrant_list)} registrants:", ""]
            
            for registrant in registrant_list[:10]:
                lines.extend([
                    f"• {registrant.get('first_name')} {registrant.get('last_name')}",
                    f"  Email: {registrant.get('email')}",
                    f"  Registrant ID: {registrant.get('id')}",
                    f"  Status: {registrant.get('status')}",
                    f"  Created: {registrant.get('create_time', 'N/A')}",
                    ""
                ])
            
            if len(registrant_list) > 10:
                lines.append(f"... and {len(registrant_list) - 10} more registrants")
            
            lines.append("")
            lines.append("💡 To delete a registrant, use the 'Registrant ID' shown above")
            
            return [TextContent(type="text", text=format_list_output(lines))]
        
        elif name == "find_registrant_by_email":
            registrants = await api_manager.list_webinar_registrants(
                arguments["webinar_id"],
                status="approved",
                page_size=300  # Get more results to search
            )
            
            registrant_list = registrants.get("registrants", [])
            search_email = arguments["email"].lower()
            
            found = None
            for registrant in registrant_list:
                if registrant.get('email', '').lower() == search_email:
                    found = registrant
                    break
            
            if found:
                lines = [
                    "Registrant Found!",
                    "",
                    f"Name: {found.get('first_name')} {found.get('last_name')}",
                    f"Email: {found.get('email')}",
                    f"Registrant ID: {found.get('id')}",
                    f"Status: {found.get('status')}",
                    f"Created: {found.get('create_time', 'N/A')}",
                    "",
                    "To delete this registrant, use:",
                    f"  Tool: delete_webinar_registrant",
                    f"  webinar_id: {arguments['webinar_id']}",
                    f"  registrant_id: {found.get('id')}"
                ]
                return [TextContent(type="text", text=format_list_output(lines))]
            else:
                return [TextContent(
                    type="text",
                    text=f"No registrant found with email: {arguments['email']}\n"
                         f"in webinar {arguments['webinar_id']}\n\n"
                         f"Use 'list_webinar_registrants' to see all registrants."
                )]
        
        elif name == "list_panelists":
            panelists = await api_manager.list_panelists(arguments["webinar_id"])
            
            panelist_list = panelists.get("panelists", [])
            if not panelist_list:
                result = f"No panelists found for webinar {arguments['webinar_id']}"
            else:
                lines = [f"Found {len(panelist_list)} panelists:", ""]
                for panelist in panelist_list:
                    lines.extend([
                        f"• {panelist.get('name')} ({panelist.get('email')})",
                        f"  ID: {panelist.get('id')}",
                        ""
                    ])
                result = format_list_output(lines)
            
            return [TextContent(type="text", text=result)]
        
        # DELETE methods - Removal tools
        elif name == "delete_webinar":
            await api_manager.delete_webinar(
                arguments["webinar_id"],
                arguments.get("occurrence_id"),
                arguments.get("cancel_webinar_reminder", False)
            )
            
            return [TextContent(
                type="text",
                text=f"Webinar {arguments['webinar_id']} deleted successfully!"
            )]
        
        elif name == "remove_panelist":
            await api_manager.remove_panelist(
                arguments["webinar_id"],
                arguments["panelist_id"]
            )
            
            return [TextContent(
                type="text",
                text=f"Panelist {arguments['panelist_id']} removed from webinar {arguments['webinar_id']}"
            )]
        
        elif name == "delete_webinar_registrant":
            await api_manager.delete_webinar_registrant(
                arguments["webinar_id"],
                arguments["registrant_id"]
            )
            
            return [TextContent(
                type="text",
                text=f"Registrant {arguments['registrant_id']} deleted successfully from webinar {arguments['webinar_id']}"
            )]
        
        # PATCH methods - Update tools
        elif name == "update_webinar":
            update_details = WebinarUpdateDetails(
                topic=arguments.get("topic"),
                start_time=arguments.get("start_time"),
                duration=arguments.get("duration"),
                agenda=arguments.get("agenda"),
                password=arguments.get("password")
            )
            
            result = await api_manager.update_webinar(arguments["webinar_id"], update_details)
            
            return [TextContent(
                type="text",
                text=f"Webinar {arguments['webinar_id']} updated successfully!\n"
                     f"Updated fields: {', '.join(result.get('updated_fields', []))}"
            )]
        
        elif name == "update_webinar_status":
            await api_manager.update_webinar_status(
                arguments["webinar_id"],
                arguments["action"],
                arguments.get("occurrence_id")
            )
            
            return [TextContent(
                type="text",
                text=f"Webinar {arguments['webinar_id']} {arguments['action']} successfully!"
            )]
        
        # Natural language processing tools
        elif name == "schedule_webinar_from_prompt":
            prompt = arguments["prompt"]
            user_selection = arguments["user_selection"]
            
            try:
                selected_user = await api_manager.get_user_by_selection(user_selection)
            except Exception as e:
                logger.error(f"User selection failed: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"User selection error: {str(e)}"
                )]
            
            webinar_details = api_manager.parse_prompt(prompt)
            webinar = await api_manager.create_webinar(selected_user['id'], webinar_details)
            
            lines = [
                "Webinar Scheduled from Prompt!",
                f"User: {selected_user.get('email')} ({selected_user.get('id')})",
                "",
                f"Prompt: \"{prompt}\"",
                "",
                "Parsed Details:",
                f"Topic: {webinar['topic']}",
                f"Start Time: {webinar['start_time']}",
                f"Duration: {webinar['duration']} minutes",
                "",
                f"Webinar ID: {webinar['id']}",
                f"Join URL: {webinar['join_url']}",
                f"Start URL: {webinar['start_url']}"
            ]
            
            return [TextContent(type="text", text=format_list_output(lines))]
        
        elif name == "schedule_recurring_webinar_from_prompt":
            prompt = arguments["prompt"]
            user_selection = arguments["user_selection"]
            
            try:
                selected_user = await api_manager.get_user_by_selection(user_selection)
            except Exception as e:
                logger.error(f"User selection failed: {e}", exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"User selection error: {str(e)}"
                )]
            
            webinar_details = api_manager.parse_recurring_prompt(prompt)
            webinar = await api_manager.create_recurring_webinar(selected_user['id'], webinar_details)
            
            lines = [
                "Recurring Webinar Scheduled from Prompt!",
                f"User: {selected_user.get('email')}",
                "",
                f"Prompt: \"{prompt}\"",
                "",
                "Parsed Details:",
                f"Topic: {webinar['topic']}",
                f"Start Time: {webinar['start_time']} (IST)",
                f"Duration: {webinar['duration']} minutes",
                f"Recurrence: {webinar.get('recurrence', {})}",
                f"Total Occurrences: {len(webinar.get('occurrences', []))}",
                "",
                f"Join URL: {webinar['join_url']}"
            ]
            
            return [TextContent(type="text", text=format_list_output(lines))]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except ConfigurationError as e:
        logger.error(f"Configuration error in tool {name}: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Configuration Error: {str(e)}\nPlease check your Zoom API credentials."
        )]
    
    except Exception as e:
        logger.error(f"Error in tool {name} with arguments {arguments}: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}\n\nArguments: {json.dumps(arguments, indent=2)}"
        )]


async def main():
    """Main server function with auto-configuration attempt"""
    global api_manager
    
    logger.info(f"Starting {SERVER_NAME} v{SERVER_VERSION}")
    
    # Try to auto-configure from environment on startup
    try:
        env_config = load_config_from_env()
        if env_config:
            await initialize_api_manager(env_config)
            logger.info("Auto-configured Zoom API from environment variables")
        else:
            logger.info("Environment variables not found. Manual configuration required.")
    except Exception as e:
        logger.warning(f"Auto-configuration failed: {e}", exc_info=True)
    
    try:
        # Run the server using stdio transport
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Server started successfully")
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=SERVER_NAME,
                    server_version=SERVER_VERSION,
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise
    finally:
        logger.info("Cleaning up resources...")
        await cleanup_api_manager()
        logger.info("Server shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"\nFATAL ERROR: {e}", file=sys.stderr)
        sys.exit(1)