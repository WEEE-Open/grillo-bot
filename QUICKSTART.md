# Quick Start Guide

Get the Grillo Telegram Bot up and running in 5 minutes!

**Note:** This bot is compatible with both the `main` and `schedule` branches of [WEEE-Open/grillo](https://github.com/WEEE-Open/grillo).

## Prerequisites

- Nix package manager installed (or Python 3.11+)
- A Telegram account
- Access to a Grillo instance

## Step 1: Get Your Credentials

### Telegram Bot Token

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Follow the prompts to create your bot
4. Copy the token that BotFather gives you

### Grillo API Token

1. Go to your Grillo instance web interface
2. Log in
3. Navigate to: **Settings** → **API Tokens**
4. Click **Create Token**
5. Set permissions to **Read-Write** (or higher)
6. Copy the generated token

## Step 2: Clone and Configure

```bash
# Clone the repository
git clone <your-repo-url>
cd grillo-bot

# Copy the example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Add your tokens to `.env`:
```env
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
GRILLO_API_TOKEN=your_token:your_password_from_grillo
GRILLO_API_URL=https://your-grillo-instance.com/api/v1
```

## Step 3: Run the Bot

### Using Nix (Recommended)

```bash
nix develop
python bot.py
```

### Using pip

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python bot.py
```

## Step 4: Test the Bot

1. Open Telegram
2. Search for your bot by username
3. Send `/start`
4. Try a command like `/locations`

## Common Commands

- `/status` - Check who's in the lab
- `/ring` - Ring for entry
- `/login` - Clock in
- `/logout Fixed the bug` - Clock out with summary
- `/bookings` - View your bookings
- `/code` - Generate entry code

## Troubleshooting

**Bot doesn't respond?**
- Check that the bot token is correct
- Verify the bot is running without errors in the terminal

**API errors?**
- Check the Grillo API token has correct permissions
- Verify the API URL ends with `/v1`
- Make sure you can access the Grillo instance from your network

**Nix issues?**
- Make sure flakes are enabled: `nix-env --version`
- Try: `nix flake update`

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check [.github/copilot-instructions.md](.github/copilot-instructions.md) for development guidelines
- Explore the Grillo API:
  - [Main branch](https://github.com/WEEE-Open/grillo)
  - [Schedule branch](https://github.com/WEEE-Open/grillo/tree/schedule) - Enhanced scheduling features

## Getting Help

- Check the [Grillo repository](https://github.com/WEEE-Open/grillo) for API docs
- Open an issue if you find bugs
- Join the WEEE-Open community!

---

Happy hacking! 🦗
