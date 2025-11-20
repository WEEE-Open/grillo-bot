"""
Grillo Telegram Bot - Main bot file with command handlers.

This bot allows interaction with the WEEE-Open/grillo API via Telegram.
"""
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

from config import config
from grillo_client import GrilloClient, get_user_client_by_telegram
from user_mapper import user_mapper

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


handlers = []

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE, pre: str = "") -> None:
    """Send a message when the command /help is issued."""

    await update.effective_message.reply_html(
        pre +
        "<b>Available commands:</b>\n"
        "/help - Show this help message\n"
        "/status - Check current lab status\n"
        "/clockin - Clock in to the lab\n"
        "/clockout - Clock out from the lab\n"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    telegram_id = user.id

    # Check if user is mapped
    is_mapped = user_mapper.is_user_mapped(telegram_id)
    print(is_mapped)
    mapping_status = ""
    if not is_mapped:
        res = user_mapper.map_user(telegram_id)
        if res:
            mapping_status = "\n\n<b>Successfully linked your account to {ldap_user}!</b>"
        else:
            mapping_status = (
                "\n\n<b>Not authenticated</b>\n"
            )

    await help(update, context, f"🦗 <b>Welcome to Grillo Bot, {user.mention_html()}!</b>\n{mapping_status}\n\n")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: # TODO check, function is as from Copilot
    """Check the status of the default lab location."""
    try:
        grillo = get_user_client_by_telegram(update.effective_user.id)
        location_id = " ".join(context.args) if context.args else "default"
        location = grillo.get_location(location_id)

        response = f"📊 <b>Status for {location['name']}</b>\n\n"

        # People in the lab
        people = location.get("people", [])
        if people:
            response += "👥 <b>People in lab:</b>\n"
            for person in people:
                response += f"  • {person.get('name', 'Unknown')}\n"
        else:
            response += "👥 No one is currently in the lab.\n"

        # Upcoming bookings
        bookings = location.get("bookings", [])
        if bookings:
            response += "\n📅 <b>Upcoming bookings:</b>\n"
            for booking in bookings[:5]:  # Show max 5
                start = datetime.fromtimestamp(booking['startTime'])
                response += f"  • {start.strftime('%a %H:%M')} - {booking.get('userName', 'Unknown')}\n"

        await update.effective_message.reply_html(response)
    except Exception as e:
        logger.error(f"Error fetching status: {e}")
        await update.effective_message.reply_text(f"❌ Error fetching status: {str(e)}")

async def clockin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clock in to the lab."""
    try:
        grillo = get_user_client_by_telegram(update.effective_user.id)
        if context.args:
            admin = grillo.is_admin()
            if admin:
                grillo = GrilloClient(user_id=context.args[0], api_token=config.GRILLO_API_TOKEN)
                location = context.args[1] if len(context.args) > 1 else None
            else:
                location=  context.args[0]
        else:
            location = None

        result = grillo.clockin(location)

        loc_name = result.get("location", "the lab")
        await update.effective_message.reply_text(f"✅ Clocked in to {loc_name}!")
    except Exception as e:
        logger.error(f"Error clocking in: {e}")
        await update.effective_message.reply_text(f"❌ Error clocking in: {str(e)}")


async def clockout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clock out from the lab."""
    if not context.args:
        await update.effective_message.reply_text(
            "❌ Please provide a summary of your work.\n"
            "Usage: /clockout <summary>"
        )
        return

    try:
        grillo = get_user_client_by_telegram(update.effective_user.id)
        summary = " ".join(context.args)
        res = grillo.clockout(summary)
        endTime = int(res.get("endTime", 0))
        startTime = int(res.get("startTime", 0))
        duration = endTime - startTime
        hours = duration // 3600
        minutes = (duration % 3600) // 60
        time_str = "Spent "
        if hours > 0:
            time_str += f"{hours}h "
        time_str += f"{minutes}m in the lab."

        await update.effective_message.reply_text(f"✅ Clocked out successfully!\n{time_str}")
    except Exception as e:
        logger.error(f"Error clocking out: {e}")
        await update.effective_message.reply_text(f"❌ Error clocking out: {str(e)}")

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    await update.effective_message.reply_text(
        "❌ Command not recognized.\n\n"
        "Use /help to see available commands."
    )


def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error(f"Update {update} caused error {context.error}")


def main() -> None:
    """Start the bot."""
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return

    # Create the Application
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    handlers = [
        start,
        help,
        status,
        clockin,
        clockout,
    ]
    aliases = {
        "info": help,
        "login": clockin,
        "logout": clockout,
        "inlab": status,
    }
    for handler in handlers:
        application.add_handler(
            CommandHandler(
                handler.__name__,
                handler,
                filters=filters.UpdateType.MESSAGE | filters.UpdateType.EDITED_MESSAGE
            )
        )
    for handler in aliases.keys():
        application.add_handler(
            CommandHandler(
                handler,
                aliases[handler],
                filters=filters.UpdateType.MESSAGE | filters.UpdateType.EDITED_MESSAGE
            )
        )

    # must be last
    application.add_handler(
        MessageHandler(
            filters.COMMAND & (filters.UpdateType.MESSAGE | filters.UpdateType.EDITED_MESSAGE),
            unknown_command
        )
    )

    # Register error handler
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("Starting Grillo Telegram Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
