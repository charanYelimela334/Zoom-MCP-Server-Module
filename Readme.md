# Zoom Webinar MCP Server

A comprehensive Model Context Protocol (MCP) server for managing Zoom webinars with a modular architecture. This server provides complete webinar lifecycle management through a clean, organized API.

## 🌟 Features

### Core Capabilities
- **Webinar Management**: Create, update, delete, and retrieve webinar information
- **Recurring Webinars**: Full support for recurring webinar schedules
- **Panelist Management**: Add, update, and remove webinar panelists
- **Registration Management**: Handle registrant approvals, denials, and cancellations
- **Polls & Surveys**: Create and manage webinar polls and surveys
- **Q&A Tracking**: Retrieve Q&A data from past webinars
- **Participant Analytics**: Track attendees and absentees
- **Token Management**: Automatic OAuth token caching and refresh

### Architecture Highlights
- **Modular Design**: Organized by HTTP methods (GET, POST, PATCH, DELETE)
- **Async/Await**: Full asynchronous support for high performance
- **Type Safety**: Pydantic models for data validation
- **File-based Token Caching**: Persistent token storage with automatic refresh
- **Timezone Support**: IST (Asia/Kolkata) timezone with UTC conversion
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## 📋 Prerequisites

- Python 3.8 or higher
- Zoom account with API credentials
- Server-to-Server OAuth app configured in Zoom Marketplace

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd zoom-webinar
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   ZOOM_ACCOUNT_ID=your_account_id
   ZOOM_CLIENT_ID=your_client_id
   ZOOM_CLIENT_SECRET=your_client_secret
   ```

## 📁 Project Structure

```
zoom-webinar/
├── zoom_mcp_server.py      # Main MCP server implementation
├── zoom_api_manager.py     # Unified API manager
├── auth.py                 # Authentication & token management
├── get_methods.py          # GET operations (retrieve data)
├── post_methods.py         # POST operations (create resources)
├── patch_methods.py        # PATCH operations (update resources)
├── delete_methods.py       # DELETE operations (remove resources)
├── requirements.txt        # Python dependencies
├── .env                    # Environment configuration
└── Access Token.txt        # Token cache file (auto-generated)
```

## 🔧 Configuration

### Zoom API Setup

1. Go to [Zoom App Marketplace](https://marketplace.zoom.us/)
2. Create a **Server-to-Server OAuth** app
3. Note your **Account ID**, **Client ID**, and **Client Secret**
4. Add required scopes:
   - `webinar:read:admin`
   - `webinar:write:admin`
   - `user:read:admin`

### Token Caching

The server automatically caches access tokens in `Access Token.txt` with:
- Token expiration tracking
- Automatic refresh before expiry
- IST timezone display for convenience

## 🎯 Usage

### Starting the Server

```bash
python zoom_mcp_server.py
```

The server runs as an MCP server using stdio transport.

### Available Tools

#### Configuration Tools
- **`auto_configure_zoom`**: Auto-configure from environment variables
- **`configure_zoom`**: Manually configure with credentials
- **`get_token_status`**: Check token status and expiry
- **`refresh_token`**: Force refresh access token

#### User Management
- **`list_users_for_selection`**: List users with numbers for selection
- **`get_users`**: Get account users

#### Webinar Creation (POST)
- **`create_webinar`**: Create a standard webinar
- **`create_webinar_interactive`**: Create with user selection
- **`create_recurring_webinar`**: Create recurring webinar
- **`add_panelists`**: Add panelists to webinar
- **`create_webinar_poll`**: Create webinar poll
- **`create_webinar_invite_links`**: Generate invite links

#### Webinar Retrieval (GET)
- **`list_webinars`**: List webinars for a user
- **`get_webinar`**: Get webinar details
- **`list_webinar_registrants`**: Get registrant list
- **`list_panelists`**: Get panelist list
- **`get_webinar_polls`**: Get webinar polls
- **`list_webinar_participants`**: Get past webinar participants
- **`list_webinar_qa`**: Get Q&A from past webinar
- **`get_webinar_absentees`**: Get registered but absent users

#### Webinar Updates (PATCH)
- **`update_webinar`**: Update webinar details
- **`update_webinar_registrant_status`**: Approve/deny/cancel registrants
- **`update_webinar_status`**: Start/end/cancel webinar

#### Webinar Deletion (DELETE)
- **`delete_webinar`**: Delete a webinar
- **`remove_panelist`**: Remove specific panelist
- **`remove_all_panelists`**: Remove all panelists
- **`delete_webinar_registrant`**: Delete a registrant

### Resources

The server exposes these resources:
- **`zoom://config`**: Current configuration status
- **`zoom://token-status`**: Token status and expiry
- **`zoom://users`**: Account users list
- **`zoom://env-status`**: Environment variables status

## 📝 Code Examples

### Creating a Webinar

```python
from zoom_api_manager import ZoomAPIManager, load_config_from_env
from post_methods import WebinarDetails

# Load configuration
config = load_config_from_env()

# Initialize manager
async with ZoomAPIManager(config) as manager:
    # Create webinar
    webinar = WebinarDetails(
        topic="Python Workshop",
        duration=90,
        agenda="Learn Python basics",
        timezone="Asia/Kolkata"
    )
    
    result = await manager.create_webinar(
        user_id="user@example.com",
        webinar_details=webinar
    )
    
    print(f"Webinar created: {result['join_url']}")
```

### Listing Webinars

```python
async with ZoomAPIManager(config) as manager:
    webinars = await manager.list_webinars(
        user_id="user@example.com",
        page_size=30,
        webinar_type="scheduled"
    )
    
    for webinar in webinars['webinars']:
        print(f"{webinar['topic']} - {webinar['start_time']}")
```

### Adding Panelists

```python
from post_methods import PanelistDetails

async with ZoomAPIManager(config) as manager:
    panelists = [
        PanelistDetails(email="panelist1@example.com", name="John Doe"),
        PanelistDetails(email="panelist2@example.com", name="Jane Smith")
    ]
    
    result = await manager.add_panelists(
        webinar_id="123456789",
        panelists=panelists
    )
```

## 🔐 Security

- **Never commit** `.env` file or `Access Token.txt` to version control
- Store credentials securely
- Use environment variables for production deployments
- Token file is automatically managed and refreshed

## 📊 Logging

Logs are written to:
- **File**: `zoom_mcp_server.log`
- **Console**: stderr output

Log levels can be adjusted in the code (default: DEBUG for file, INFO for console).

## 🛠️ Module Details

### `auth.py`
- OAuth 2.0 authentication
- File-based token caching
- Automatic token refresh
- Timezone-aware expiry tracking

### `zoom_api_manager.py`
- Unified interface to all operations
- User selection helpers
- Natural language prompt parsing
- Datetime parsing utilities

### `get_methods.py`
- List webinars (scheduled/upcoming)
- Get webinar details
- Retrieve participants, registrants, panelists
- Access Q&A and poll data

### `post_methods.py`
- Create webinars (standard & recurring)
- Add panelists
- Create polls and surveys
- Generate invite links

### `patch_methods.py`
- Update webinar details
- Manage registrant status
- Update webinar status (start/end/cancel)
- Modify panelists and polls

### `delete_methods.py`
- Delete webinars
- Remove panelists
- Delete registrants
- Remove polls and surveys

### `zoom_mcp_server.py`
- MCP server implementation
- Tool and resource handlers
- Error handling and validation
- Server lifecycle management

## 🐛 Troubleshooting

### Token Issues
- Check `.env` file has correct credentials
- Verify token file permissions
- Check `zoom_mcp_server.log` for errors
- Use `refresh_token` tool to force refresh

### API Errors
- Ensure required Zoom scopes are enabled
- Verify user IDs and webinar IDs are correct
- Check rate limits (Zoom API has rate limiting)
- Review logs for detailed error messages

### Timezone Issues
- Default timezone is IST (Asia/Kolkata)
- Times are automatically converted to UTC for API
- Token expiry displays in IST for convenience

## 📄 License

[Add your license here]

## 👥 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For issues and questions:
- Check the logs in `zoom_mcp_server.log`
- Review Zoom API documentation
- Open an issue in the repository

## 🔄 Version History

### Version 3.0.1 (Current)
- Modular architecture with separated HTTP methods
- File-based token caching
- Timezone-aware datetime handling
- Comprehensive error handling
- Full async/await support

## 🙏 Acknowledgments

- Built with [MCP (Model Context Protocol)](https://modelcontextprotocol.io/)
- Uses [Zoom API v2](https://developers.zoom.us/docs/api/)
- Powered by [httpx](https://www.python-httpx.org/) and [Pydantic](https://pydantic-docs.helpmanual.io/)

---

# Zoom Webinar API - OAuth Scopes Reference

**Version:** 1.0  
**Last Updated:** October 2025  
**API Server Version:** 3.0.1

## Overview

This document provides a comprehensive reference of all OAuth scopes required for each API endpoint implemented in the Zoom Webinar MCP Server. OAuth scopes are permissions that determine what actions an application can perform on behalf of a Zoom account.

## Table of Contents

1. [Scope Types](#scope-types)
2. [Authentication & Token Management](#authentication--token-management)
3. [User Management](#user-management)
4. [Webinar Creation (POST Methods)](#webinar-creation-post-methods)
5. [Webinar Information Retrieval (GET Methods)](#webinar-information-retrieval-get-methods)
6. [Webinar Updates (PATCH Methods)](#webinar-updates-patch-methods)
7. [Webinar Deletion (DELETE Methods)](#webinar-deletion-delete-methods)
8. [Configuration Guide](#configuration-guide)

## Scope Types

### Core Scopes

| Scope | Description | Level |
|-------|-------------|-------|
| `user:read:admin` | Read all user information | Admin |
| `user:write:admin` | Create and manage users | Admin |
| `webinar:read:admin` | View all user webinars | Admin |
| `webinar:write:admin` | View and manage all user webinars | Admin |
| `webinar:read` | View user's own webinars | User |
| `webinar:write` | Create and manage user's own webinars | User |
| `webinar:master` | Master scope for webinar operations | Master |
| `meeting:read:admin` | View all user meetings | Admin |
| `meeting:write:admin` | View and manage all user meetings | Admin |
| `report:read:admin` | View reports and analytics | Admin |
| `recording:write:admin` | Manage all user recordings | Admin |

### Scope Hierarchy

- **Admin Scopes** (`*:admin`): Full access to all users' resources
- **User Scopes** (without `admin`): Access to only authenticated user's resources
- **Master Scopes** (`*:master`): Legacy scopes with broad permissions

## Authentication & Token Management

### Token Status Check

- **Endpoint:** `GET /token-status`
- **Scopes Required:** None (Internal operation)
- **Description:** Checks the current access token status without making API calls. Works with any valid token.

### Token Refresh

- **Endpoint:** `POST /refresh_token`
- **Scopes Required:** None (Internal operation)
- **Description:** Forces regeneration of the access token. Requires existing valid token.

## User Management

### List All Users

- **Endpoint:** `GET /users`
- **HTTP Method:** GET
- **Zoom API:** `GET /users`
- **Required Scopes:**
  - `user:read:admin` (Recommended)
  - `user:read` (Minimum for own profile)
- **Description:** Retrieves list of all users in the Zoom account with pagination support.
- **Parameters:**
  - `page_size`: Number of results per page (max 300)
  - `page_number`: Page number for pagination
  - `status`: Filter by user status (active, inactive, pending)

### Get Specific User

- **Endpoint:** `GET /users/{user_id}`
- **HTTP Method:** GET
- **Zoom API:** `GET /users/{user_id}`
- **Required Scopes:**
  - `user:read:admin` (For any user)
  - `user:read` (For own profile only)
- **Description:** Retrieves detailed information for a specific user.

## Webinar Creation (POST Methods)

### Create Single Webinar

- **Endpoint:** `POST /users/{user_id}/webinars`
- **HTTP Method:** POST
- **Zoom API:** `POST /users/{user_id}/webinars`
- **Required Scopes:**
  - `webinar:write` (For own webinars)
  - `webinar:write:admin` (For any user's webinars)
- **Recommended:** `[webinar:write:admin, user:read:admin]`
- **Description:** Creates a scheduled webinar with specified topic, start time, duration, and settings.

### Create Recurring Webinar

- **Endpoint:** `POST /users/{user_id}/webinars` (with recurrence)
- **HTTP Method:** POST
- **Zoom API:** `POST /users/{user_id}/webinars` (type: 9)
- **Required Scopes:**
  - `webinar:write` (For own recurring webinars)
  - `webinar:write:admin` (For any user's recurring webinars)
- **Description:** Creates a recurring webinar with daily, weekly, or monthly schedule.

### Add Panelists to Webinar

- **Endpoint:** `POST /webinars/{webinar_id}/panelists`
- **HTTP Method:** POST
- **Zoom API:** `POST /webinars/{webinar_id}/panelists`
- **Required Scopes:**
  - `webinar:write` (For own webinars)
  - `webinar:write:admin` (For any user's webinars)
- **Description:** Adds one or multiple panelists (co-hosts) to a webinar.

### Create Webinar Poll

- **Endpoint:** `POST /webinars/{webinar_id}/polls`
- **HTTP Method:** POST
- **Zoom API:** `POST /webinars/{webinar_id}/polls`
- **Required Scopes:**
  - `webinar:write` (For own webinars)
  - `webinar:write:admin` (For any user's webinars)
- **Description:** Creates a poll that can be used during a webinar.

### Create Webinar Invite Links

- **Endpoint:** `POST /webinars/{webinar_id}/invite_links`
- **HTTP Method:** POST
- **Zoom API:** `POST /webinars/{webinar_id}/invite_links`
- **Required Scopes:**
  - `webinar:write` (For own webinars)
  - `webinar:write:admin` (For any user's webinars)
- **Description:** Generates shareable invitation links for a webinar.

## Webinar Information Retrieval (GET Methods)

### List User's Webinars

- **Endpoint:** `GET /users/{user_id}/webinars`
- **HTTP Method:** GET
- **Zoom API:** `GET /users/{user_id}/webinars`
- **Required Scopes:**
  - `webinar:read` (For own webinars)
  - `webinar:read:admin` (For all user's webinars)
- **Description:** Lists all webinars for a specific user with pagination and filtering.

### Get Specific Webinar Details

- **Endpoint:** `GET /webinars/{webinar_id}`
- **HTTP Method:** GET
- **Zoom API:** `GET /webinars/{webinar_id}`
- **Required Scopes:**
  - `webinar:read` (For own webinars)
  - `webinar:read:admin` (For any user's webinars)
- **Description:** Retrieves full details of a specific webinar.

### List Webinar Registrants

- **Endpoint:** `GET /webinars/{webinar_id}/registrants`
- **HTTP Method:** GET
- **Zoom API:** `GET /webinars/{webinar_id}/registrants`
- **Required Scopes:**
  - `webinar:read` (For own webinars)
  - `webinar:read:admin` (For any user's webinars)
- **Description:** Lists all registrants for a webinar with their registration details.

### List Panelists

- **Endpoint:** `GET /webinars/{webinar_id}/panelists`
- **HTTP Method:** GET
- **Zoom API:** `GET /webinars/{webinar_id}/panelists`
- **Required Scopes:**
  - `webinar:read` (For own webinars)
  - `webinar:read:admin` (For any user's webinars)
- **Description:** Lists all panelists for a webinar.

### List Webinar Q&A

- **Endpoint:** `GET /past_webinars/{webinar_id}/qa`
- **HTTP Method:** GET
- **Zoom API:** `GET /past_webinars/{webinar_id}/qa`
- **Required Scopes:**
  - `webinar:read` (For own webinars)
  - `webinar:read:admin` (For any user's webinars)
- **Description:** Retrieves Q&A from a past/completed webinar.
- **Note:** Only available for webinars that have already occurred.

### List Webinar Participants

- **Endpoint:** `GET /past_webinars/{webinar_uuid}/participants`
- **HTTP Method:** GET
- **Zoom API:** `GET /past_webinars/{webinar_uuid}/participants`
- **Required Scopes:**
  - `webinar:read` (For own webinars)
  - `webinar:read:admin` (For any user's webinars)
- **Description:** Lists participants who attended a past webinar.
- **Note:** Uses webinar UUID instead of ID.

### Get Webinar Absentees

- **Endpoint:** `GET /past_webinars/{webinar_uuid}/absentees`
- **HTTP Method:** GET
- **Zoom API:** `GET /past_webinars/{webinar_uuid}/absentees`
- **Required Scopes:**
  - `webinar:read` (For own webinars)
  - `webinar:read:admin` (For any user's webinars)
- **Description:** Lists registrants who did not attend a past webinar.

## Webinar Updates (PATCH Methods)

### Update Webinar Details

- **Endpoint:** `PATCH /webinars/{webinar_id}`
- **HTTP Method:** PATCH
- **Zoom API:** `PATCH /webinars/{webinar_id}`
- **Required Scopes:**
  - `webinar:write` (For own webinars)
  - `webinar:write:admin` (For any user's webinars)
- **Description:** Updates webinar settings including topic, agenda, schedule, and password.

### Update Webinar Status

- **Endpoint:** `PATCH /webinars/{webinar_id}/status`
- **HTTP Method:** PATCH
- **Zoom API:** `PATCH /webinars/{webinar_id}/status`
- **Required Scopes:**
  - `webinar:write` (For own webinars)
  - `webinar:write:admin` (For any user's webinars)
- **Description:** Changes webinar status: "start", "end", or "cancel".

### Update Registrant Status

- **Endpoint:** `PATCH /webinars/{webinar_id}/registrants/status`
- **HTTP Method:** PATCH
- **Zoom API:** `PATCH /webinars/{webinar_id}/registrants/status`
- **Required Scopes:**
  - `webinar:write` (For own webinars)
  - `webinar:write:admin` (For any user's webinars)
- **Description:** Approves, cancels, or denies webinar registrations in bulk.

## Webinar Deletion (DELETE Methods)

### Delete Webinar

- **Endpoint:** `DELETE /webinars/{webinar_id}`
- **HTTP Method:** DELETE
- **Zoom API:** `DELETE /webinars/{webinar_id}`
- **Required Scopes:**
  - `webinar:write` (For own webinars)
  - `webinar:write:admin` (For any user's webinars)
- **Description:** Permanently deletes a webinar. Cannot be undone.
- **⚠️ Warning:** This action is permanent and cannot be reversed.

### Delete Webinar Registrant

- **Endpoint:** `DELETE /webinars/{webinar_id}/registrants/{registrant_id}`
- **HTTP Method:** DELETE
- **Zoom API:** `DELETE /webinars/{webinar_id}/registrants/{registrant_id}`
- **Required Scopes:**
  - `webinar:write` (For own webinars)
  - `webinar:write:admin` (For any user's webinars)
- **Description:** Removes a registrant from a webinar.

### Remove Panelist

- **Endpoint:** `DELETE /webinars/{webinar_id}/panelists/{panelist_id}`
- **HTTP Method:** DELETE
- **Zoom API:** `DELETE /webinars/{webinar_id}/panelists/{panelist_id}`
- **Required Scopes:**
  - `webinar:write` (For own webinars)
  - `webinar:write:admin` (For any user's webinars)
- **Description:** Removes a panelist from a webinar.

### Remove All Panelists

- **Endpoint:** `DELETE /webinars/{webinar_id}/panelists`
- **HTTP Method:** DELETE
- **Zoom API:** `DELETE /webinars/{webinar_id}/panelists`
- **Required Scopes:**
  - `webinar:write` (For own webinars)
  - `webinar:write:admin` (For any user's webinars)
- **Description:** Removes all panelists from a webinar in one operation.

## Configuration Guide

### Minimum Scope Configuration

For a basic webinar management application using Server-to-Server OAuth:

```
Minimum Scopes Required:
- webinar:write:admin
- webinar:read:admin
- user:read:admin
```

### Recommended Scope Configuration

For full functionality with all endpoints:

```
Recommended Scopes:
- webinar:write:admin    (Create, update, delete webinars)
- webinar:read:admin     (List and view webinar details)
- user:read:admin        (List and view user information)
```

### Setting Up OAuth Scopes

**In Zoom App Marketplace:**

1. Navigate to [Zoom App Marketplace](https://marketplace.zoom.us/)
2. Click "Develop" → "Build App"
3. Select "Server-to-Server OAuth" as the app type
4. Under "Scopes" section, add required scopes:
   - Click "Add Scopes"
   - Search for and select:
     - `webinar:write:admin`
     - `webinar:read:admin`
     - `user:read:admin`
5. Click "Continue" and complete app setup
6. Copy your credentials:
   - Account ID
   - Client ID
   - Client Secret

**Environment Variables Setup:**

Create a `.env` file in your project root:

```bash
# .env
ZOOM_ACCOUNT_ID=your_account_id_here
ZOOM_CLIENT_ID=your_client_id_here
ZOOM_CLIENT_SECRET=your_client_secret_here
```

**Initializing the API Manager:**

```python
from zoom_api_manager import ZoomAPIManager, load_config_from_env

# Auto-load from .env
config = load_config_from_env()
api_manager = ZoomAPIManager(config)
```

### Scope-Based Access Control

| Method | Read Scope | Write Scope |
|--------|-----------|-------------|
| GET (List/Retrieve) | `webinar:read:admin` or `webinar:read` | N/A |
| POST (Create) | N/A | `webinar:write:admin` or `webinar:write` |
| PATCH (Update) | N/A | `webinar:write:admin` or `webinar:write` |
| DELETE (Remove) | N/A | `webinar:write:admin` or `webinar:write` |

### Admin vs User Scopes

**Admin Scopes (`*:admin`):**
- Full access to all users' resources
- Typically used for Server-to-Server OAuth applications
- Required for managing other users' webinars
- Recommended for backend services and automation

**User Scopes (without `admin`):**
- Access only to authenticated user's resources
- Used for OAuth flows where user authorizes the app
- Cannot access other users' webinars
- Recommended for user-facing applications

### Scope Combinations

#### Scenario 1: Manage Your Own Webinars Only
**Required Scopes:** `[webinar:read, webinar:write]`  
**Use Case:** Personal webinar management app

#### Scenario 2: Manage All Account Webinars (Backend Service)
**Required Scopes:** `[webinar:read:admin, webinar:write:admin, user:read:admin]`  
**Use Case:** Company-wide webinar automation system

#### Scenario 3: View Only (Reporting/Analytics)
**Required Scopes:** `[webinar:read:admin, user:read:admin]`  
**Use Case:** Dashboard and reporting application

#### Scenario 4: Full Management with Accounts API (Enterprise)
**Required Scopes:** `[webinar:read:admin, webinar:write:admin, user:read:admin, user:write:admin, account:read, account:write]`  
**Use Case:** Multi-account management system

## Testing Scopes

To verify your application has the correct scopes:

1. **Check Token Status:**
   ```python
   status = await api_manager.get_token_status()
   print(status)
   ```

2. **Test Read Operations First:**
   Start with a GET endpoint to verify read scopes are working

3. **Test Write Operations:**
   Attempt a POST/PATCH/DELETE to verify write scopes

4. **Review Error Messages:**
   Zoom API returns 403 Forbidden if scopes are insufficient:
   ```json
   {
     "code": 1001,
     "message": "User not authorized",
     "errors": "The user does not have the appropriate scopes."
   }
   ```

## Scope-Permission Matrix

| Operation | webinar:read | webinar:read:admin | webinar:write | webinar:write:admin | user:read | user:read:admin |
|-----------|--------------|-------------------|---------------|-------------------|-----------|----------------|
| List own webinars | ✅ | ✅ | - | - | - | - |
| List all webinars | ❌ | ✅ | - | - | - | - |
| View webinar details | ✅ | ✅ | - | - | - | - |
| Create webinar (own) | - | - | ✅ | ✅ | - | - |
| Create webinar (any) | - | - | ❌ | ✅ | - | - |
| Update webinar (own) | - | - | ✅ | ✅ | - | - |
| Update webinar (any) | - | - | ❌ | ✅ | - | - |
| Delete webinar (own) | - | - | ✅ | ✅ | - | - |
| Delete webinar (any) | - | - | ❌ | ✅ | - | - |
| List registrants | ✅ | ✅ | - | - | - | - |
| Add/Remove registrants | - | - | ✅ | ✅ | - | - |
| List all users | - | - | - | - | ❌ | ✅ |
| View user details | ✅ | ✅ | - | - | ❌ | ✅ |

**Legend:** ✅ = Permission granted | ❌ = Permission denied | - = Not applicable

## Best Practices

### 1. Use Minimal Scopes
Only request scopes your application actually needs. This follows the principle of least privilege and improves security.

```python
# Good: Only admin read/write
scopes = ["webinar:read:admin", "webinar:write:admin"]

# Avoid: Requesting unnecessary scopes
scopes = ["*"]  # Don't do this
```

### 2. Handle Token Expiration
Scopes don't expire, but tokens do. Implement proper token refresh:

```python
token_status = await api_manager.get_token_status()
if token_status["status"] != "valid":
    await api_manager.refresh_token()
```

### 3. Validate Scope Access
Before attempting operations, check if you have the right scopes:

```python
async def safely_create_webinar(user_id, details):
    try:
        return await api_manager.create_webinar(user_id, details)
    except Exception as e:
        if "insufficient" in str(e).lower():
            print("Error: webinar:write:admin scope required")
            raise
```

### 4. Log Scope Information
Keep audit logs of scope usage for compliance:

```python
logger.info(f"Token expires at: {await api_manager.get_token_status()}")
```

### 5. Document Required Scopes
Always document scope requirements in your code:

```python
"""
Create a new webinar.

Required Scopes:
  - webinar:write (for own webinars)
  - webinar:write:admin (for any user's webinars)

Args:
    user_id: User ID to create webinar for
    webinar_details: WebinarDetails object
    
Returns:
    dict: Created webinar information
"""
```

## Troubleshooting

### Issue: Scope Changes Not Taking Effect

**Cause:** Token cache contains old scopes

**Solution:**
1. Delete the token file: `rm "Access Token.txt"`
2. Restart the application
3. Token will be regenerated with new scopes

### Issue: Cannot Create Webinars for Other Users

**Cause:** Using `webinar:write` instead of `webinar:write:admin`

**Solution:**
```python
# This requires webinar:write:admin
await api_manager.create_webinar("other_user_id", webinar_details)

# This works with webinar:write
await api_manager.create_webinar("my_own_user_id", webinar_details)
```

### Issue: Cannot List Other Users' Webinars

**Cause:** Using `webinar:read` instead of `webinar:read:admin`

**Solution:**
```python
# This requires webinar:read:admin for other users
await api_manager.list_webinars("other_user_id")

# This works with webinar:read for own webinars
await api_manager.list_webinars("my_own_user_id")
```

## Additional Resources

- [Zoom OAuth Scopes Documentation](https://developers.zoom.us/docs/integrations/oauth-scopes/)
- [Zoom API Reference](https://developers.zoom.us/docs/api/)
- [Zoom App Marketplace](https://marketplace.zoom.us/)
- [Server-to-Server OAuth Setup](https://developers.zoom.us/docs/internal-apps/)

## Changelog

### Version 1.0 (October 2025)
- Initial documentation
- Comprehensive scope matrix for all endpoints
- Best practices and troubleshooting guide
- Configuration examples for common scenarios
Zoom Webinar API - OAuth Scopes Reference
Version: 1.0
Last Updated: October 2025
API Server Version: 3.0.1
Overview
This document provides a comprehensive reference of all OAuth scopes required for each API endpoint implemented in the Zoom Webinar MCP Server. OAuth scopes are permissions that determine what actions an application can perform on behalf of a Zoom account.

Table of Contents

Scope Types
Authentication & Token Management
User Management
Webinar Creation (POST Methods)
Webinar Information Retrieval (GET Methods)
Webinar Updates (PATCH Methods)
Webinar Deletion (DELETE Methods)
Configuration Guide


Scope Types
Core Scopes
ScopeDescriptionLeveluser:read:adminRead all user informationAdminuser:write:adminCreate and manage usersAdminwebinar:read:adminView all user webinarsAdminwebinar:write:adminView and manage all user webinarsAdminwebinar:readView user's own webinarsUserwebinar:writeCreate and manage user's own webinarsUserwebinar:masterMaster scope for webinar operationsMastermeeting:read:adminView all user meetingsAdminmeeting:write:adminView and manage all user meetingsAdminreport:read:adminView reports and analyticsAdminrecording:write:adminManage all user recordingsAdmin
Scope Hierarchy

Admin Scopes (*:admin): Full access to all users' resources
User Scopes (* without admin): Access to only authenticated user's resources
Master Scopes (*:master): Legacy scopes with broad permissions


Authentication & Token Management
Token Status Check
Endpoint: GET /token-status
Scopes Required: None (Internal operation)
Required Scopes: [None]
Recommended: Any active OAuth scope
Description: Checks the current access token status without making API calls. Works with any valid token.

Token Refresh
Endpoint: POST /refresh_token
Scopes Required: None (Internal operation)
Required Scopes: [None]
Recommended: Any active OAuth scope
Description: Forces regeneration of the access token. Requires existing valid token.

User Management
List All Users
Endpoint: GET /users
HTTP Method: GET
Zoom API: GET /users
Required Scopes:
  - user:read:admin (Recommended)
  - user:read (Minimum for own profile)

Minimum Scope Set: [user:read:admin]
Description: Retrieves list of all users in the Zoom account with pagination support. Returns user emails, IDs, types, and status.
Parameters:

page_size: Number of results per page (max 300)
page_number: Page number for pagination
status: Filter by user status (active, inactive, pending)


Get Specific User
Endpoint: GET /users/{user_id}
HTTP Method: GET
Zoom API: GET /users/{user_id}
Required Scopes:
  - user:read:admin (For any user)
  - user:read (For own profile only)

Recommended Scope Set: [user:read:admin]
Description: Retrieves detailed information for a specific user including contact details, settings, and account type.

Get User by Selection (Interactive)
Endpoint: POST /get_user_by_selection
HTTP Method: Custom (Internal wrapper)
Required Scopes:
  - user:read:admin

Minimum Scope Set: [user:read:admin]
Description: Helper function to locate users by number, name, email, or ID. Requires listing all users first.

Webinar Creation (POST Methods)
Create Single Webinar
Endpoint: POST /users/{user_id}/webinars
HTTP Method: POST
Zoom API: POST /users/{user_id}/webinars
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin, user:read:admin]
Description: Creates a scheduled webinar with specified topic, start time, duration, and settings.
Parameters:

topic: Webinar title (required)
start_time: ISO 8601 format datetime (optional, defaults to 1 hour from now)
duration: Duration in minutes (default: 60)
timezone: Timezone for display (default: UTC)
agenda: Webinar description
password: Webinar access password
host_video: Enable host video (default: true)
panelists_video: Enable panelist video (default: false)
registration_type: Registration requirement (0=disabled, 1=required, 2=optional)
auto_recording: Recording option (none, local, cloud)


Create Recurring Webinar
Endpoint: POST /users/{user_id}/webinars (with recurrence)
HTTP Method: POST
Zoom API: POST /users/{user_id}/webinars (type: 9)
Required Scopes:
  - webinar:write (For own recurring webinars)
  - webinar:write:admin (For any user's recurring webinars)

Recommended Scope Set: [webinar:write:admin, user:read:admin]
Description: Creates a recurring webinar with daily, weekly, or monthly schedule.
Parameters:

topic: Webinar title (required)
start_time: ISO 8601 format datetime (required)
duration: Duration in minutes (default: 60)
recurrence_type: 1=Daily, 2=Weekly, 3=Monthly
repeat_interval: How often to repeat (default: 1)
weekly_days: For weekly: comma-separated day numbers (1=Sun, 2=Mon, etc.)
monthly_day: For monthly: specific day of month
end_times: Number of occurrences
end_date_time: End date for recurrence


Add Panelists to Webinar
Endpoint: POST /webinars/{webinar_id}/panelists
HTTP Method: POST
Zoom API: POST /webinars/{webinar_id}/panelists
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin]
Description: Adds one or multiple panelists (co-hosts) to a webinar. Panelists receive invitations.
Parameters:

webinar_id: ID of target webinar (required)
panelist_emails: Array of email addresses (required)


Create Webinar Poll
Endpoint: POST /webinars/{webinar_id}/polls
HTTP Method: POST
Zoom API: POST /webinars/{webinar_id}/polls
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin]
Description: Creates a poll that can be used during a webinar. Includes questions and answer options.
Parameters:

webinar_id: ID of target webinar (required)
poll_title: Title of the poll (required)
questions: Array of question objects with title and answer options (required)


Create Webinar Invite Links
Endpoint: POST /webinars/{webinar_id}/invite_links
HTTP Method: POST
Zoom API: POST /webinars/{webinar_id}/invite_links
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin]
Description: Generates shareable invitation links for a webinar with time-to-live settings.
Parameters:

webinar_id: ID of target webinar (required)
ttl: Time to live in seconds (default: 7200, 2 hours)


Webinar Information Retrieval (GET Methods)
List User's Webinars
Endpoint: GET /users/{user_id}/webinars
HTTP Method: GET
Zoom API: GET /users/{user_id}/webinars
Required Scopes:
  - webinar:read (For own webinars)
  - webinar:read:admin (For all user's webinars)

Recommended Scope Set: [webinar:read:admin, user:read:admin]
Description: Lists all webinars for a specific user with pagination and filtering options.
Parameters:

user_id: User ID (required)
page_size: Results per page (default: 30, max: 300)
page_number: Page number (default: 1)
type: Filter type - "scheduled" (default) or "upcoming"


Get Specific Webinar Details
Endpoint: GET /webinars/{webinar_id}
HTTP Method: GET
Zoom API: GET /webinars/{webinar_id}
Required Scopes:
  - webinar:read (For own webinars)
  - webinar:read:admin (For any user's webinars)

Recommended Scope Set: [webinar:read:admin]
Description: Retrieves full details of a specific webinar including settings, status, URLs, and occurrence information.
Parameters:

webinar_id: Webinar ID (required)
occurrence_id: For recurring webinars (optional)
show_previous_occurrences: Include past occurrences (default: false)


List Webinar Registrants
Endpoint: GET /webinars/{webinar_id}/registrants
HTTP Method: GET
Zoom API: GET /webinars/{webinar_id}/registrants
Required Scopes:
  - webinar:read (For own webinars)
  - webinar:read:admin (For any user's webinars)

Recommended Scope Set: [webinar:read:admin]
Description: Lists all registrants for a webinar with their registration details, status, and timestamps.
Parameters:

webinar_id: Webinar ID (required)
status: Filter by status - "approved", "pending", "denied", "cancelled" (default: "approved")
page_size: Results per page (default: 30, max: 300)
page_number: Page number (default: 1)
occurrence_id: For recurring webinars (optional)


Find Registrant by Email
Endpoint: GET /webinars/{webinar_id}/registrants (filtered)
HTTP Method: GET (custom wrapper)
Zoom API: GET /webinars/{webinar_id}/registrants
Required Scopes:
  - webinar:read (For own webinars)
  - webinar:read:admin (For any user's webinars)

Recommended Scope Set: [webinar:read:admin]
Description: Helper function to find a specific registrant by email address within a webinar.
Parameters:

webinar_id: Webinar ID (required)
email: Registrant email address (required)


Get Specific Registrant
Endpoint: GET /webinars/{webinar_id}/registrants/{registrant_id}
HTTP Method: GET
Zoom API: GET /webinars/{webinar_id}/registrants/{registrant_id}
Required Scopes:
  - webinar:read (For own webinars)
  - webinar:read:admin (For any user's webinars)

Recommended Scope Set: [webinar:read:admin]
Description: Retrieves complete details for a single registrant including custom question answers.
Parameters:

webinar_id: Webinar ID (required)
registrant_id: Registrant ID (required)
occurrence_id: For recurring webinars (optional)


List Panelists
Endpoint: GET /webinars/{webinar_id}/panelists
HTTP Method: GET
Zoom API: GET /webinars/{webinar_id}/panelists
Required Scopes:
  - webinar:read (For own webinars)
  - webinar:read:admin (For any user's webinars)

Recommended Scope Set: [webinar:read:admin]
Description: Lists all panelists for a webinar including their names, emails, and IDs.

List Webinar Polls
Endpoint: GET /webinars/{webinar_id}/polls
HTTP Method: GET
Zoom API: GET /webinars/{webinar_id}/polls
Required Scopes:
  - webinar:read (For own webinars)
  - webinar:read:admin (For any user's webinars)

Recommended Scope Set: [webinar:read:admin]
Description: Retrieves all polls created for a webinar with their questions and answer options.

Get Specific Poll
Endpoint: GET /webinars/{webinar_id}/polls/{poll_id}
HTTP Method: GET
Zoom API: GET /webinars/{webinar_id}/polls/{poll_id}
Required Scopes:
  - webinar:read (For own webinars)
  - webinar:read:admin (For any user's webinars)

Recommended Scope Set: [webinar:read:admin]
Description: Retrieves detailed information for a specific poll including all questions.

List Webinar Q&A
Endpoint: GET /past_webinars/{webinar_id}/qa
HTTP Method: GET
Zoom API: GET /past_webinars/{webinar_id}/qa
Required Scopes:
  - webinar:read (For own webinars)
  - webinar:read:admin (For any user's webinars)

Recommended Scope Set: [webinar:read:admin]
Description: Retrieves Q&A (questions and answers) from a past/completed webinar, including participant names and timestamps.
Note: Only available for webinars that have already occurred.

List Webinar Participants
Endpoint: GET /past_webinars/{webinar_uuid}/participants
HTTP Method: GET
Zoom API: GET /past_webinars/{webinar_uuid}/participants
Required Scopes:
  - webinar:read (For own webinars)
  - webinar:read:admin (For any user's webinars)

Recommended Scope Set: [webinar:read:admin]
Description: Lists participants who attended a past webinar with join/leave times and duration attended.
Note: Only available for webinars that have already occurred. Uses webinar UUID instead of ID.

Get Webinar Absentees
Endpoint: GET /past_webinars/{webinar_uuid}/absentees
HTTP Method: GET
Zoom API: GET /past_webinars/{webinar_uuid}/absentees
Required Scopes:
  - webinar:read (For own webinars)
  - webinar:read:admin (For any user's webinars)

Recommended Scope Set: [webinar:read:admin]
Description: Lists registrants who did not attend a past webinar.
Note: Only available for webinars that have already occurred.

List Registration Questions
Endpoint: GET /webinars/{webinar_id}/registrants/questions
HTTP Method: GET
Zoom API: GET /webinars/{webinar_id}/registrants/questions
Required Scopes:
  - webinar:read (For own webinars)
  - webinar:read:admin (For any user's webinars)

Recommended Scope Set: [webinar:read:admin]
Description: Retrieves custom registration questions configured for a webinar.

Get Webinar Survey
Endpoint: GET /webinars/{webinar_id}/survey
HTTP Method: GET
Zoom API: GET /webinars/{webinar_id}/survey
Required Scopes:
  - webinar:read (For own webinars)
  - webinar:read:admin (For any user's webinars)

Recommended Scope Set: [webinar:read:admin]
Description: Retrieves survey settings and questions for a webinar.

Get Webinar Tracking Sources
Endpoint: GET /webinars/{webinar_id}/tracking_sources
HTTP Method: GET
Zoom API: GET /webinars/{webinar_id}/tracking_sources
Required Scopes:
  - webinar:read (For own webinars)
  - webinar:read:admin (For any user's webinars)

Recommended Scope Set: [webinar:read:admin]
Description: Retrieves tracking sources (URL parameters) configured for the webinar for analytics.

Get Live Stream Settings
Endpoint: GET /webinars/{webinar_id}/livestream
HTTP Method: GET
Zoom API: GET /webinars/{webinar_id}/livestream
Required Scopes:
  - webinar:read (For own webinars)
  - webinar:read:admin (For any user's webinars)

Recommended Scope Set: [webinar:read:admin]
Description: Retrieves live stream configuration if the webinar is set up for live streaming.

Get Webinar Invite Links
Endpoint: GET /webinars/{webinar_id}/invite_links
HTTP Method: GET
Zoom API: GET /webinars/{webinar_id}/invite_links
Required Scopes:
  - webinar:read (For own webinars)
  - webinar:read:admin (For any user's webinars)

Recommended Scope Set: [webinar:read:admin]
Description: Retrieves generated invite links for a webinar.

Webinar Updates (PATCH Methods)
Update Webinar Details
Endpoint: PATCH /webinars/{webinar_id}
HTTP Method: PATCH
Zoom API: PATCH /webinars/{webinar_id}
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin]
Description: Updates webinar settings including topic, agenda, schedule, password, and feature settings.
Updatable Fields:

topic: Webinar title
agenda: Webinar description
start_time: Start time in ISO 8601 format
duration: Duration in minutes
timezone: Display timezone
password: Access password
host_video: Enable/disable host video
panelists_video: Enable/disable panelist video
approval_type: Registration approval type
registration_type: Registration requirement
auto_recording: Recording option
alternative_hosts: Comma-separated emails


Update Webinar Status
Endpoint: PATCH /webinars/{webinar_id}/status
HTTP Method: PATCH
Zoom API: PATCH /webinars/{webinar_id}/status
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin]
Description: Changes webinar status: "start" (begin webinar), "end" (stop webinar), or "cancel" (cancel webinar).
Parameters:

webinar_id: Webinar ID (required)
action: "start", "end", or "cancel" (required)
occurrence_id: For recurring webinars (optional)


Update Registrant Status
Endpoint: PATCH /webinars/{webinar_id}/registrants/status
HTTP Method: PATCH
Zoom API: PATCH /webinars/{webinar_id}/registrants/status
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin]
Description: Approves, cancels, or denies webinar registrations in bulk.
Parameters:

webinar_id: Webinar ID (required)
action: "approve", "cancel", or "deny" (required)
registrants: List of registrant objects with id and email (required)


Update Panelist
Endpoint: PATCH /webinars/{webinar_id}/panelists/{panelist_id}
HTTP Method: PATCH
Zoom API: PATCH /webinars/{webinar_id}/panelists/{panelist_id}
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin]
Description: Updates panelist information (name and/or email).
Parameters:

webinar_id: Webinar ID (required)
panelist_id: Panelist ID (required)
name: Panelist name (optional)
email: Panelist email (optional)


Update Webinar Poll
Endpoint: PATCH /webinars/{webinar_id}/polls/{poll_id}
HTTP Method: PATCH
Zoom API: PATCH /webinars/{webinar_id}/polls/{poll_id}
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin]
Description: Updates poll settings and questions.

Update Live Stream Settings
Endpoint: PATCH /webinars/{webinar_id}/livestream
HTTP Method: PATCH
Zoom API: PATCH /webinars/{webinar_id}/livestream
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin]
Description: Updates live stream configuration (YouTube, Facebook, etc.).

Update Webinar Survey
Endpoint: PATCH /webinars/{webinar_id}/survey
HTTP Method: PATCH
Zoom API: PATCH /webinars/{webinar_id}/survey
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin]
Description: Updates post-webinar survey settings and questions.

Update Registration Questions
Endpoint: PATCH /webinars/{webinar_id}/registrants/questions
HTTP Method: PATCH
Zoom API: PATCH /webinars/{webinar_id}/registrants/questions
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin]
Description: Updates custom registration questions for a webinar.

Update Webinar Branding
Endpoint: PATCH /webinars/{webinar_id}/branding
HTTP Method: PATCH
Zoom API: PATCH /webinars/{webinar_id}/branding
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin]
Description: Updates webinar branding elements (logo, colors, etc.).

Webinar Deletion (DELETE Methods)
Delete Webinar
Endpoint: DELETE /webinars/{webinar_id}
HTTP Method: DELETE
Zoom API: DELETE /webinars/{webinar_id}
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin]
Description: Permanently deletes a webinar. Cannot be undone. Optionally sends cancellation notice to registrants.
Parameters:

webinar_id: Webinar ID (required)
occurrence_id: For recurring webinars (optional)
cancel_webinar_reminder: Send cancellation email (default: false)

Warning: This action is permanent and cannot be reversed.

Delete Webinar Registrant
Endpoint: DELETE /webinars/{webinar_id}/registrants/{registrant_id}
HTTP Method: DELETE
Zoom API: DELETE /webinars/{webinar_id}/registrants/{registrant_id}
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin]
Description: Removes a registrant from a webinar. Registrant cannot attend. Optionally sends notification.
Parameters:

webinar_id: Webinar ID (required)
registrant_id: Registrant ID (required) - Use list_webinar_registrants or find_registrant_by_email to obtain
occurrence_id: For recurring webinars (optional)


Delete Batch Registrants
Endpoint: DELETE /webinars/{webinar_id}/registrants (with body)
HTTP Method: DELETE
Zoom API: DELETE /webinars/{webinar_id}/registrants
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin]
Description: Removes multiple registrants from a webinar in a single operation.
Parameters:

webinar_id: Webinar ID (required)
registrant_ids: Array of registrant IDs (required)
occurrence_id: For recurring webinars (optional)


Remove Panelist
Endpoint: DELETE /webinars/{webinar_id}/panelists/{panelist_id}
HTTP Method: DELETE
Zoom API: DELETE /webinars/{webinar_id}/panelists/{panelist_id}
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin]
Description: Removes a panelist from a webinar.
Parameters:

webinar_id: Webinar ID (required)
panelist_id: Panelist ID (required)


Remove All Panelists
Endpoint: DELETE /webinars/{webinar_id}/panelists
HTTP Method: DELETE
Zoom API: DELETE /webinars/{webinar_id}/panelists
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin]
Description: Removes all panelists from a webinar in one operation.
Parameters:

webinar_id: Webinar ID (required)


Delete Webinar Poll
Endpoint: DELETE /webinars/{webinar_id}/polls/{poll_id}
HTTP Method: DELETE
Zoom API: DELETE /webinars/{webinar_id}/polls/{poll_id}
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin]
Description: Deletes a poll from a webinar.

Delete Webinar Survey
Endpoint: DELETE /webinars/{webinar_id}/survey
HTTP Method: DELETE
Zoom API: DELETE /webinars/{webinar_id}/survey
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin]
Description: Removes the post-webinar survey from a webinar.

Delete Tracking Source
Endpoint: DELETE /webinars/{webinar_id}/tracking_sources/{source_id}
HTTP Method: DELETE
Zoom API: DELETE /webinars/{webinar_id}/tracking_sources/{source_id}
Required Scopes:
  - webinar:write (For own webinars)
  - webinar:write:admin (For any user's webinars)

Recommended Scope Set: [webinar:write:admin]
Description: Deletes a tracking source from a webinar.

Configuration Guide
Minimum Scope Configuration
For a basic webinar management application using Server-to-Server OAuth:
Minimum Scopes Required:
- webinar:write:admin
- webinar:read:admin
- user:read:admin
Recommended Scope Configuration
For full functionality with all endpoints:
Recommended Scopes:
- webinar:write:admin    (Create, update, delete webinars)
- webinar:read:admin     (List and view webinar details)
- user:read:admin        (List and view user information)
Setting Up OAuth Scopes
In Zoom App Marketplace:

Navigate to Zoom App Marketplace
Click "Develop" → "Build App"
Select "Server-to-Server OAuth" as the app type
Under "Scopes" section, add required scopes:

Click "Add Scopes"
Search for and select:

webinar:write:admin
webinar:read:admin
user:read:admin




Click "Continue" and complete app setup
Copy your credentials:

Account ID
Client ID
Client Secret



Environment Variables Setup:
Create a .env file in your project root:
bash# .env
ZOOM_ACCOUNT_ID=your_account_id_here
ZOOM_CLIENT_ID=your_client_id_here
ZOOM_CLIENT_SECRET=your_client_secret_here
Initializing the API Manager:
pythonfrom zoom_api_manager import ZoomAPIManager, ZoomConfig

# Auto-load from .env
config = ZoomConfig(
    account_id="your_account_id",
    client_id="your_client_id",
    client_secret="your_client_secret"
)

api_manager = ZoomAPIManager(config)
Scope-Based Access Control
The following table shows which HTTP methods require which scopes:
MethodRead ScopeWrite ScopeGET (List/Retrieve)webinar:read:admin or webinar:readN/APOST (Create)N/Awebinar:write:admin or webinar:writePATCH (Update)N/Awebinar:write:admin or webinar:writeDELETE (Remove)N/Awebinar:write:admin or webinar:write
Admin vs User Scopes
Admin Scopes (*:admin):

Full access to all users' resources
Typically used for Server-to-Server OAuth applications
Required for managing other users' webinars
Recommended for backend services and automation

User Scopes (without admin):

Access only to authenticated user's resources
Used for OAuth flows where user authorizes the app
Cannot access other users' webinars
Recommended for user-facing applications

Scope Combinations
Scenario 1: Manage Your Own Webinars Only
Required Scopes: [webinar:read, webinar:write]
Use Case: Personal webinar management app
Scenario 2: Manage All Account Webinars (Backend Service)
Required Scopes: [webinar:read:admin, webinar:write:admin, user:read:admin]
Use Case: Company-wide webinar automation system
Scenario 3: View Only (Reporting/Analytics)
Required Scopes: [webinar:read:admin, user:read:admin]
Use Case: Dashboard and reporting application
Scenario 4: Full Management with Accounts API (Enterprise)
Required Scopes: [webinar:read:admin, webinar:write:admin, user:read:admin, user:write:admin, account:read, account:write]
Use Case: Multi-account management system
Testing Scopes
To verify your application has the correct scopes:

Check Token Status:

python   status = await api_manager.get_token_status()
   print(status)

Test Read Operations First:
Start with a GET endpoint to verify read scopes are working
Test Write Operations:
Attempt a POST/PATCH/DELETE to verify write scopes
Review Error Messages:
Zoom API returns 403 Forbidden if scopes are insufficient:

json   {
     "code": 1001,
     "message": "User not authorized",
     "errors": "The user does not have the appropriate scopes."
   }
Scope-Permission Matrix
Below is a comprehensive matrix showing which scopes enable which operations:
Operationwebinar:readwebinar:read:adminwebinar:writewebinar:write:adminuser:readuser:read:adminList own webinars✅✅----List all webinars❌✅----View webinar details✅✅----Create webinar (own)--✅✅--Create webinar (any)--❌✅--Update webinar (own)--✅✅--Update webinar (any)--❌✅--Delete webinar (own)--✅✅--Delete webinar (any)--❌✅--List registrants✅✅----Add/Remove registrants--✅✅--List all users----❌✅View user details✅✅--❌✅
Legend: ✅ = Permission granted | ❌ = Permission denied | - = Not applicable

Error Handling & Scope Issues
Common Scope-Related Errors
Error: "Insufficient Scopes"
json{
  "code": 1001,
  "message": "User not authorized",
  "errors": "Insufficient scopes to perform this operation."
}
Solution:

Verify scopes in Zoom App Marketplace
Refresh your access token
Restart the application to load new scopes

Error: "Authorization Failed"
json{
  "code": 1000,
  "message": "Invalid access token"
}
Solution:

Check if token has expired
Regenerate credentials
Verify Account ID, Client ID, and Client Secret

Debugging Scope Issues
Enable debug logging to see scope information:
pythonimport logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("zoom-auth")
Check the token cache file for scope information:
bash# View cached token
cat "Access Token.txt"

Best Practices
1. Use Minimal Scopes
Only request scopes your application actually needs. This follows the principle of least privilege and improves security.
python# Good: Only admin read/write
scopes = ["webinar:read:admin", "webinar:write:admin"]

# Avoid: Requesting unnecessary scopes
scopes = ["*"]  # Don't do this
2. Handle Scope Expiration
Scopes don't expire, but tokens do. Implement proper token refresh:
pythontoken_status = await api_manager.get_token_status()
if token_status["status"] != "valid":
    await api_manager.refresh_token()
3. Validate Scope Access
Before attempting operations, check if you have the right scopes:
pythonasync def safely_create_webinar(user_id, details):
    try:
        return await api_manager.create_webinar(user_id, details)
    except Exception as e:
        if "insufficient" in str(e).lower():
            print("Error: webinar:write:admin scope required")
            raise
4. Log Scope Information
Keep audit logs of scope usage for compliance:
pythonlogger.info(f"Using scopes: {config.get_scopes()}")
logger.info(f"Token expires at: {await api_manager.get_token_status()}")
5. Separate Read and Write Operations
Structure your code to clearly separate read and write operations:
pythonclass WebinarManager:
    async def read_webinar_data(self):
        # Uses webinar:read:admin
        return await self.api.list_webinars(user_id)
    
    async def write_webinar_data(self, webinar_id, updates):
        # Uses webinar:write:admin
        return await self.api.update_webinar(webinar_id, updates)
6. Document Required Scopes
Always document scope requirements in your code and API documentation:
python"""
Create a new webinar.

Required Scopes:
  - webinar:write (for own webinars)
  - webinar:write:admin (for any user's webinars)

Args:
    user_id: User ID to create webinar for
    webinar_details: WebinarDetails object
    
Returns:
    dict: Created webinar information
"""

Troubleshooting
Issue: Scope Changes Not Taking Effect
Cause: Token cache contains old scopes
Solution:

Delete the token file:

bash   rm "Access Token.txt"

Restart the application
Token will be regenerated with new scopes

Issue: Cannot Create Webinars for Other Users
Cause: Using webinar:write instead of webinar:write:admin
Solution:
python# This requires webinar:write:admin
await api_manager.create_webinar("other_user_id", webinar_details)

# This works with webinar:write
await api_manager.create_webinar("my_own_user_id", webinar_details)
Issue: Registrant Operations Failing
Cause: Missing write scopes for registrant management
Solution:
All registrant operations (add, remove, update status) require write scopes:

webinar:write (for own webinars)
webinar:write:admin (for any webinar)

Issue: Cannot List Other Users' Webinars
Cause: Using webinar:read instead of webinar:read:admin
Solution:
python# This requires webinar:read:admin for other users
await api_manager.list_webinars("other_user_id")

# This works with webinar:read for own webinars
await api_manager.list_webinars("my_own_user_id")

Scope Renewal & Token Refresh
Automatic Token Caching
The Zoom API Manager includes file-based token caching that automatically:

Caches access tokens to avoid unnecessary API calls
Tracks token expiration time
Automatically refreshes tokens before they expire
Stores token metadata including IST timezone display

Manual Token Refresh
python# Force refresh token
status = await api_manager.refresh_token()
print(f"Token valid until: {status['expires_at_ist']}")
Token Expiration
Zoom access tokens expire in 3600 seconds (1 hour) by default. The system includes a 5-minute buffer to proactively refresh before expiration.
python# Check remaining time
status = await api_manager.get_token_status()
if status['remaining_minutes'] < 10:
    await api_manager.refresh_token()

Additional Resources

Zoom OAuth Scopes Documentation
Zoom API Reference
Zoom App Marketplace
Server-to-Server OAuth Setup
Zoom Security Whitepaper


Changelog
Version 1.0 (October 2025)

Initial documentation
Comprehensive scope matrix for all endpoints
Best practices and troubleshooting guide
Configuration examples for common scenarios