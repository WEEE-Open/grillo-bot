# 🦗 Grillo Telegram Bot

A Telegram bot for interacting with the [WEEE-Open/grillo](https://github.com/WEEE-Open/grillo) lab booking and management API.

**Compatible with:** `main` and `schedule` branches of WEEE-Open/grillo

## Features

- 📍 **List locations** - View all available lab locations
- 📊 **Check status** - See who's in the lab and upcoming bookings
- 🔔 **Ring for entry** - Ring the WEEETofono to request lab access
- ⏰ **Clock in/out** - Track your lab time with audits
- 📅 **Manage bookings** - View and manage lab bookings
- 📆 **View events** - See upcoming lab events
- 🔑 **Generate codes** - Create temporary entry codes

## Prerequisites

- Python 3.11 or higher
- Nix package manager (optional, for reproducible development environment)
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- A Grillo API Token (from the Grillo web UI settings)

## Setup

### Option 1: Using Nix Flake (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/grillo-bot.git
cd grillo-bot
```

2. Enter the nix development shell:
```bash
nix develop
```

3. Copy the example environment file and configure it:
```bash
cp .env.example .env
```

4. Edit `.env` and add your credentials:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GRILLO_API_TOKEN=your_grillo_api_token_here
GRILLO_API_URL=https://grillo.weeeopen.it/api/v1
```

5. Run the bot:
```bash
python bot.py
```

### Option 2: Using pip/virtualenv

1. Clone the repository:
```bash
git clone https://github.com/yourusername/grillo-bot.git
cd grillo-bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Copy and configure the environment file:
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. Run the bot:
```bash
python bot.py
```

## Getting API Credentials

### Telegram Bot Token

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow the instructions
3. Copy the bot token provided

### Grillo API Token

1. Log in to the Grillo web interface
2. Navigate to Settings → API Tokens
3. Click "Create Token"
4. Choose permissions (the bot needs at least Read-Write access)
5. Copy the generated token

## Bot Commands

Once the bot is running, you can interact with it using these commands:

### User Management

| Command | Description |
|---------|-------------|
| `/link [username]` | Link your Telegram account to LDAP. If username is omitted, the bot attempts to auto-discover your account via Telegram ID (if configured in LDAP). |

**Important:** Most commands require you to link your Telegram account first. Try `/link` first for auto-discovery, or use `/link <your_ldap_username>` for manual linking.

### General Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and command list |
| `/help` | Show available commands |

### Lab Operations

| Command | Description |
|---------|-------------|
| `/locations` | List all lab locations |
| `/status [location]` | Check current lab status and occupancy |
| `/ring [location]` | Ring the WEEETofono to request entry |
| `/login [location]` | Clock in to the lab (requires linked account) |
| `/logout <summary>` | Clock out with work summary (requires linked account) |
| `/bookings` | View your bookings for the week (requires linked account) |
| `/events` | View upcoming events |
| `/code` | Generate a temporary entry code (requires linked account) |

## Project Structure

```
grillo-bot/
├── bot.py              # Main bot file with command handlers
├── grillo_client.py    # API client for Grillo endpoints
├── user_mapper.py      # Telegram to LDAP user mapping
├── config.py           # Configuration management
├── flake.nix           # Nix flake for development environment
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variables template
├── .env                # Your configuration (not in git)
├── user_mapping.json   # User mappings (not in git, auto-created)
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## User Authentication

The bot uses a hybrid authentication system:

1. **Admin API Token** - Used for server-level operations (listing locations, events, etc.)
2. **User Sessions** - Generated per-user for authenticated operations (login, logout, bookings, codes)
3. **UID Parameter** - All API token requests include a `uid` query parameter for user tracking

### Linking Your Account

Before using authenticated commands, link your Telegram account:

```bash
# Auto-discovery (if Telegram ID is configured in LDAP)
/link

# Manual linking
/link your_ldap_username
```

This creates a mapping between your Telegram ID and your LDAP account in the Grillo system. The bot will then generate a session cookie for your user, allowing you to perform operations as yourself.

### How It Works

1. User sends `/link` or `/link username`
2. Bot attempts to find user by Telegram ID via `/users?telegram_id=...` endpoint (if no username provided)
3. Bot verifies the username exists in LDAP
4. Bot creates a mapping: `telegram_id -> ldap_username`
5. Bot generates a session cookie for that user
6. Future commands use that session for authentication
7. API token requests include `uid` parameter for user tracking

The mappings are stored locally in `user_mapping.json` and are not committed to git.

## Development

### Using Nix

The project includes a Nix flake that provides a reproducible development environment with all dependencies:

```bash
# Enter the development shell
nix develop

# The shell includes:
# - Python 3.11
# - All required Python packages
# - Development tools
```

### Code Style

This project follows PEP 8 style guidelines. Please ensure your code is properly formatted before committing.

### Adding New Commands

1. Create an async function in `bot.py`:
```python
async def my_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Command description."""
    # Your implementation
    await update.message.reply_text("Response")
```

2. Register the command handler in `main()`:
```python
application.add_handler(CommandHandler("mycommand", my_command))
```

### Adding New API Methods

Add methods to the `GrilloClient` class in `grillo_client.py`:

```python
def my_api_method(self, param: str) -> Dict[str, Any]:
    """Method description."""
    return self._make_request("GET", f"/endpoint/{param}")
```

## API Documentation

The bot interacts with the following Grillo API endpoints:

- `GET /locations` - List all locations
- `GET /locations/:id` - Get location details with people and bookings
- `POST /locations/:id/ring` - Ring the WEEETofono
- `GET /audits` - Get audit entries (lab time tracking)
- `POST /audits` - Clock in to the lab
- `PATCH /audits` - Clock out from the lab
- `GET /bookings` - Get bookings for the week
- `POST /bookings` - Create a new booking
- `DELETE /bookings/:id` - Delete a booking
- `GET /events` - Get upcoming events
- `POST /codes` - Generate an entry code

For more details, see the [Grillo API source code](https://github.com/WEEE-Open/grillo/tree/master/backend/api).

## Troubleshooting

### Bot doesn't respond

- Check that your `TELEGRAM_BOT_TOKEN` is correct
- Verify the bot is running without errors
- Check your internet connection

### API errors

- Verify your `GRILLO_API_TOKEN` is correct and has the right permissions
- Check that `GRILLO_API_URL` points to the correct Grillo instance
- Ensure the Grillo API is accessible from your network

### Nix issues

- Make sure you have Nix installed with flakes enabled
- Try `nix flake update` to update dependencies
- Run `nix flake check` to verify the flake

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT

## Related Projects

- [WEEE-Open/grillo](https://github.com/WEEE-Open/grillo) - The Grillo lab booking system
  - Main branch: Core functionality
  - [Schedule branch](https://github.com/WEEE-Open/grillo/tree/schedule) - Enhanced scheduling features
- [WEEEOpen](https://weeeopen.it/) - WEEE Open community

## Authors

Created for the WEEE-Open community.
