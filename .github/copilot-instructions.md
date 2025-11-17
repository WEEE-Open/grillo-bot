# Copilot Instructions - Grillo Telegram Bot

## Project Overview
Python Telegram bot for interacting with the WEEE-Open/grillo API. Provides lab status tracking, clock in/out functionality, and automatic user authentication via Telegram ID.

**Target Branch:** Compatible with both `main` and `schedule` branches of [WEEE-Open/grillo](https://github.com/WEEE-Open/grillo).

## Tech Stack
- Python 3.11+
- python-telegram-bot library for async bot functionality
- requests library with Session support for API calls
- python-dotenv for configuration management
- watchdog for development auto-reload

## Development Guidelines
- Use async/await patterns with python-telegram-bot
- Handle API errors gracefully with try/except blocks
- Follow PEP 8 style guidelines
- Keep bot commands simple and intuitive
- Use environment variables for sensitive configuration
- Never commit `.env` file or `user_mapping.json`
- Use `dev.py` for development with auto-reload
- Test all commands after changes

## Project Structure
- `bot.py` - Main bot with command handlers
- `dev.py` - Development runner with auto-reload
- `grillo_client.py` - API client for Grillo endpoints
- `user_mapper.py` - Telegram to LDAP user mapping
- `config.py` - Configuration management and validation
- `utils.py` - Utility functions
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (gitignored)
- `.env.example` - Template for environment variables
- `user_mapping.json` - User mappings (gitignored, auto-created)
- `.github/copilot-instructions.md` - This file

## Grillo API Endpoints Used
The bot interacts with the following Grillo API v1 endpoints:
- `GET /user?telegram_id=<id>` - Auto-discover user by Telegram ID
- `GET /locations/:id` - Get location details with people and bookings
- `GET /audits` - Get audit entries (time tracking)
- `POST /audits` - Clock in to lab
- `PATCH /audits` - Clock out from lab
- `POST /session` - Generate user session cookie

API Authentication:
- Admin operations: Bearer token in Authorization header
- User operations: Session cookie + optional uid parameter

## Development Setup
1. Create virtual environment: `python -m venv venv && source venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file from `.env.example`
4. Add credentials to `.env`:
   - `TELEGRAM_BOT_TOKEN` - From @BotFather
   - `GRILLO_API_TOKEN` - From Grillo web UI
   - `GRILLO_API_URL` - API endpoint (default: http://localhost:3000/api/v1)
5. Run development mode: `python dev.py` (auto-reloads on file changes)
6. Run production mode: `python bot.py`

## Bot Commands
- `/start` - Welcome message with auto-linking
- `/help` - Show available commands
- `/status [location]` - Check who's in the lab
- `/clockin [location]` - Clock in to lab
- `/clockout <summary>` - Clock out with work summary

## Key Features
- **Auto-linking**: Users are automatically linked on `/start` if their Telegram ID is in LDAP
- **Dual Authentication**: Admin API token for server ops + per-user session cookies
- **UID Tracking**: API token requests include uid parameter for user tracking
- **Auto-reload**: Development mode watches files and restarts on changes
- **Session Caching**: User sessions are cached to avoid repeated authentication

## Authentication Flow
1. User sends `/start`
2. Bot queries `/user?telegram_id=<id>` to find LDAP user
3. If found, creates mapping in `user_mapping.json`
4. Bot generates session cookie via `/session` endpoint
5. Subsequent commands use session cookie for authentication
6. API token requests include `uid` parameter when available

## Testing Checklist
- [ ] Bot starts without errors in both dev and production modes
- [ ] `/start` auto-links users correctly
- [ ] All commands respond with proper messages
- [ ] API errors are handled gracefully with user-friendly messages
- [ ] Environment variables are validated on startup
- [ ] Session cookies are cached and reused
- [ ] UID parameter is included in API token requests
- [ ] Auto-reload works in development mode
