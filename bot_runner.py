"""
Script to run the Telegram bot directly
"""

import main
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Starting Telegram bot...")
    
    # This will call the bot directly
    if hasattr(main, 'app') and main.app:
        main.app.run_polling()
    else:
        logging.error("Bot application not found in main module")