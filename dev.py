#!/usr/bin/env python3
"""
Development runner with auto-reload on file changes.

This script watches for file changes and automatically restarts the bot.
Use this for development instead of running bot.py directly.
"""
import sys
import time
import subprocess
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class BotRestartHandler(FileSystemEventHandler):
    """Handler that restarts the bot when Python files change."""

    def __init__(self, bot_process=None):
        self.bot_process = bot_process
        self.last_restart = 0
        self.debounce_seconds = 1  # Prevent multiple restarts in quick succession

    def on_modified(self, event):
        """Called when a file is modified."""
        if event.is_directory:
            return

        # Only react to Python files
        if not event.src_path.endswith('.py'):
            return

        # Debounce: ignore changes within 1 second of last restart
        current_time = time.time()
        if current_time - self.last_restart < self.debounce_seconds:
            return

        logger.info(f"Detected change in {event.src_path}")
        self.restart_bot()
        self.last_restart = current_time

    def restart_bot(self):
        """Restart the bot process."""
        if self.bot_process and self.bot_process.poll() is None:
            logger.info("Stopping bot...")
            self.bot_process.terminate()
            try:
                self.bot_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Bot didn't stop gracefully, killing...")
                self.bot_process.kill()

        logger.info("Starting bot...")
        self.bot_process = subprocess.Popen(
            [sys.executable, "bot.py"],
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        return self.bot_process


def main():
    """Run the bot with auto-reload."""
    logger.info("🦗 Starting Grillo Bot in development mode with auto-reload...")

    # Start the bot initially
    handler = BotRestartHandler()
    handler.bot_process = handler.restart_bot()

    # Set up file watcher
    observer = Observer()
    watch_path = Path(__file__).parent
    observer.schedule(handler, str(watch_path), recursive=False)
    observer.start()

    logger.info(f"👀 Watching for changes in {watch_path}")
    logger.info("Press Ctrl+C to stop")

    try:
        while True:
            time.sleep(1)
            # Check if bot process died unexpectedly
            if handler.bot_process.poll() is not None:
                logger.error("Bot process died unexpectedly, restarting...")
                handler.bot_process = handler.restart_bot()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        observer.stop()
        if handler.bot_process and handler.bot_process.poll() is None:
            handler.bot_process.terminate()
            handler.bot_process.wait()

    observer.join()


if __name__ == "__main__":
    main()
