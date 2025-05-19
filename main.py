"""
Main entry point for the Telegram verification bot application.
"""
import logging
from bot import app

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000)
