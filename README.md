# 🦗 Grillo Telegram Bot

A Telegram bot for interacting with the [WEEE-Open/grillo](https://github.com/WEEE-Open/grillo) lab booking and management API.

**Compatible with:** `main` and `schedule` branches of WEEE-Open/grillo

## Features

-  **Check status** - See who's in the lab and upcoming bookings
- ⏰ **Clock in/out** - Track your lab time with audits
- � **Auto-reload** - Development mode with automatic restart on file changes

## Prerequisites

- Python 3.11 or higher
- Nix package manager (optional, for reproducible development environment)
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- A Grillo API Token (from the Grillo web UI settings)

## Quick Start

### 1. Get Credentials

**Telegram Bot Token:**
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow the prompts
3. Copy the token

**Grillo API Token:**
1. Log in to the Grillo web interface
2. Go to Settings → API Tokens → Create Token
3. Set permissions to Read-Write
4. Copy the token

### 2. Setup

**Using Nix (Recommended):**
```bash
git clone https://github.com/yourusername/grillo-bot.git
cd grillo-bot
nix develop
cp .env.example .env
# Edit .env with your tokens
python dev.py  # Development mode with auto-reload
```

**Using pip:**
```bash
git clone https://github.com/yourusername/grillo-bot.git
cd grillo-bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your tokens
python dev.py  # Development mode with auto-reload
```

**Environment Variables (`.env`):**
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
GRILLO_API_TOKEN=your_api_token_here
GRILLO_API_URL=http://localhost:3000/api/v1
```

### 3. Run

```bash
# Development mode (auto-reloads on file changes)
python dev.py

# Production mode
python bot.py
```

### 4. Use the Bot

1. Find your bot on Telegram
2. Send `/start`
3. Your account will be auto-linked if your Telegram ID is in LDAP
4. Use `/help` to see available commands

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message - auto-links your account if Telegram ID is in LDAP |
| `/help` | Show available commands |
| `/status [location]` | Check who's in the lab and upcoming bookings |
| `/clockin [location]` | Clock in to the lab |
| `/clockout <summary>` | Clock out with work summary |

**Note:** The bot automatically links your Telegram account on `/start` if your Telegram ID is configured in the Grillo LDAP server.

## Project Structure

```
grillo-bot/
├── bot.py              # Main bot with command handlers
├── dev.py              # Development runner with auto-reload
├── grillo_client.py    # Grillo API client
├── user_mapper.py      # Telegram ↔ LDAP user mapping
├── config.py           # Configuration management
├── utils.py            # Utility functions
├── flake.nix           # Nix development environment
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
├── .env                # Your config (gitignored)
├── user_mapping.json   # User mappings (gitignored, auto-created)
└── README.md           # This file
```

## How Authentication Works

The bot uses a hybrid authentication system:

1. **Auto-Discovery**: When you send `/start`, the bot queries the Grillo API endpoint `/user?telegram_id=YOUR_ID`
2. **User Mapping**: If found, your Telegram account is automatically linked to your LDAP user
3. **Session Generation**: The bot generates a session cookie for authenticated operations
4. **UID Tracking**: All API requests include your user ID for proper tracking

**Requirements:**
- Your Telegram ID must be configured in the Grillo LDAP server
- The bot needs an admin API token to query user information

Mappings are stored locally in `user_mapping.json` (gitignored).

## Development

### Auto-Reload

Use `dev.py` for development - it automatically restarts the bot when you modify any Python file:

```bash
python dev.py
```

Features:
- Watches all `.py` files for changes
- Automatic bot restart on save
- Debouncing (1s delay to prevent rapid restarts)
- Crash recovery
- Clean shutdown with Ctrl+C

### Adding Commands

1. Add handler function in `bot.py`:
```python
async def mycommand(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    grillo = get_user_client_by_telegram(update.effective_user.id)
    # Your logic here
    await update.message.reply_text("Response")
```

2. Register in `main()`:
```python
handlers = [start, help, status, clockin, clockout, mycommand]
```

### Adding API Methods

Add to `GrilloClient` in `grillo_client.py`:

```python
def my_method(self, param: str) -> Dict[str, Any]:
    return self._make_request("GET", f"/endpoint/{param}")
```

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings to functions
- Handle errors gracefully

## Grillo API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/user?telegram_id=<id>` | GET | Auto-discover user by Telegram ID |
| `/locations/:id` | GET | Get location details with people/bookings |
| `/audits` | GET | Get audit entries (time tracking) |
| `/audits` | POST | Clock in to lab |
| `/audits` | PATCH | Clock out from lab |
| `/session` | POST | Generate user session cookie |

See the [Grillo API source](https://github.com/WEEE-Open/grillo) for complete documentation.

## Troubleshooting

**Bot not responding:**
- Verify `TELEGRAM_BOT_TOKEN` in `.env`
- Check bot is running: `ps aux | grep bot.py`
- Look for errors in terminal output

**Auto-linking fails:**
- Ensure your Telegram ID is in the Grillo LDAP server
- Check `GRILLO_API_TOKEN` has proper permissions
- Verify `GRILLO_API_URL` is correct and accessible

**Nix issues:**
- Ensure flakes are enabled: `nix-shell -p nixFlakes`
- Update flake: `nix flake update`
- Rebuild: `nix develop`

## License

MIT

## Contributing

Pull requests welcome! For major changes, please open an issue first.

## License

MIT

## Related Projects

- [WEEE-Open/grillo](https://github.com/WEEE-Open/grillo) - The Grillo lab booking system
  - Main branch: Core functionality
  - [Schedule branch](https://github.com/WEEE-Open/grillo/tree/schedule) - Enhanced scheduling features
- [WEEEOpen](https://weeeopen.it/) - WEEE Open community

## Authors

Created for the WEEE-Open community.
