"""
Grillo Telegram Bot - Main bot file with command handlers.

This bot allows interaction with the WEEE-Open/grillo API via Telegram.
"""
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import config
from grillo_client import get_user_client
from grillo_client import user_mapper

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


handlers = []

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE, pre: str = "") -> None:
    """Send a message when the command /help is issued."""

    await update.message.reply_html(
        pre +
        "<b>Available commands:</b>\n"
        "/help - Show this help message"
        "/status - Check current lab status\n"
        "/login - Clock in to the lab\n"
        "/logout - Clock out from the lab\n"
        # "/bookings - View your bookings\n"
        # "/locations - List all lab locations\n"
        # "/ring - Ring the WEEETofono to request entry\n"
        # "/events - View upcoming events\n"
        # "/code - Generate an entry code\n"
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    telegram_id = user.id

    # Check if user is mapped
    is_mapped = user_mapper.is_user_mapped(telegram_id)
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

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None: # TODO check
    """Check the status of the default lab location."""
    try:
        grillo = get_user_client(update.effective_user.id)
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

        await update.message.reply_html(response)
    except Exception as e:
        logger.error(f"Error fetching status: {e}")
        await update.message.reply_text(f"❌ Error fetching status: {str(e)}")

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clock in to the lab."""
    try:
        grillo = get_user_client(update.effective_user.id)
        if context.args:
            admin = grillo.is_admin()

        user = # self by default, if specified check for admin
        # if not admin, assume it's location instead

        location = " ".join(context.args) if context.args else None # lab by default
        result = grillo.login_to_lab(location)

        loc_name = result.get("location", "the lab")
        await update.message.reply_text(f"✅ Clocked in to {loc_name}!")
    except Exception as e:
        logger.error(f"Error logging in: {e}")
        await update.message.reply_text(f"❌ Error logging in: {str(e)}")


async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clock out from the lab."""
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a summary of your work.\n"
            "Usage: /logout <summary>"
        )
        return

    try:
        grillo = get_user_client(update.effective_user.id)
        summary = " ".join(context.args)
        grillo.logout_from_lab(summary)

        await update.message.reply_text("✅ Clocked out successfully!")
    except Exception as e:
        logger.error(f"Error logging out: {e}")
        await update.message.reply_text(f"❌ Error logging out: {str(e)}")




# async def locations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """List all available locations."""
#     try:
#         grillo = get_user_client(update.effective_user.id)
#         locations_list = grillo.get_locations()

#         if not locations_list:
#             await update.message.reply_text("No locations found.")
#             return

#         response = "📍 <b>Available Locations:</b>\n\n"
#         for loc in locations_list:
#             default_marker = " ⭐" if loc.get("default") else ""
#             response += f"• <b>{loc['name']}</b> ({loc['id']}){default_marker}\n"

#         await update.message.reply_html(response)
#     except Exception as e:
#         logger.error(f"Error fetching locations: {e}")
#         await update.message.reply_text(f"❌ Error fetching locations: {str(e)}")



# async def ring(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Ring the WEEETofono to request entry."""
#     try:
#         grillo = get_user_client(update.effective_user.id)
#         location_id = " ".join(context.args) if context.args else "default"
#         success = grillo.ring_location(location_id)

#         if success:
#             await update.message.reply_text("🔔 Ringing the WEEETofono...")
#         else:
#             await update.message.reply_text("❌ Failed to ring. The WEEETofono might be offline.")
#     except Exception as e:
#         logger.error(f"Error ringing: {e}")
#         await update.message.reply_text(f"❌ Error: {str(e)}")


# async def bookings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """View bookings for the current week."""
#     try:
#         grillo = get_user_client(update.effective_user.id)
#         bookings_list = grillo.get_bookings()

#         if not bookings_list:
#             await update.message.reply_text("📅 No bookings for this week.")
#             return

#         response = "📅 <b>Your Bookings:</b>\n\n"
#         for booking in bookings_list:
#             start = datetime.fromtimestamp(booking['startTime'])
#             end_str = ""
#             if booking.get('endTime'):
#                 end = datetime.fromtimestamp(booking['endTime'])
#                 end_str = f" - {end.strftime('%H:%M')}"

#             response += f"• {start.strftime('%a %d %b, %H:%M')}{end_str}\n"
#             response += f"  ID: {booking['id']}\n\n"

#         await update.message.reply_html(response)
#     except Exception as e:
#         logger.error(f"Error fetching bookings: {e}")
#         await update.message.reply_text(f"❌ Error fetching bookings: {str(e)}")


# async def events(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """View upcoming events."""
#     try:
#         grillo = get_user_client(update.effective_user.id)
#         events_list = grillo.get_events()

#         if not events_list:
#             await update.message.reply_text("📆 No upcoming events.")
#             return

#         response = "📆 <b>Upcoming Events:</b>\n\n"
#         for event in events_list[:10]:  # Show max 10 events
#             start = datetime.fromtimestamp(event['startTime'])
#             response += f"• <b>{event['title']}</b>\n"
#             response += f"  {start.strftime('%a %d %b, %H:%M')}\n"
#             if event.get('description'):
#                 response += f"  {event['description']}\n"
#             response += "\n"

#         await update.message.reply_html(response)
#     except Exception as e:
#         logger.error(f"Error fetching events: {e}")
#         await update.message.reply_text(f"❌ Error fetching events: {str(e)}")


# async def code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Generate an entry code."""
#     try:
#         grillo = get_user_client(update.effective_user.id)
#         result = grillo.generate_code()
#         code_value = result.get("code")

#         await update.message.reply_html(
#             f"🔑 <b>Your entry code:</b>\n\n"
#             f"<code>{code_value}</code>\n\n"
#             f"This code expires in 60 seconds.\n"
#             f"Show it at the lab entrance or scan the QR code."
#         )
#     except Exception as e:
#         logger.error(f"Error generating code: {e}")
#         await update.message.reply_text(f"❌ Error generating code: {str(e)}")


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
        login,
        logout,
        # locations,
        # bookings,
    ]
    aliases = {
        "info": help,
        "inlab": status,
    }
    for handler in handlers:
        application.add_handler(CommandHandler(handler.__name__, handler))
    for handler in aliases.keys():
        application.add_handler(CommandHandler(handler, aliases[handler]))

    # Register error handler
    application.add_error_handler(error_handler)

    # Start the bot
    logger.info("Starting Grillo Telegram Bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
