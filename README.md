# Telegram Verification Bot

A Telegram bot that restricts new group members until an admin verifies them with commands.

## Features

- Automatically restricts new members when they join a group
- Sends a message notifying the new member they need admin verification
- Admin command (/verify) to approve members and grant chat permissions
- Admin command (/reject) to remove unapproved members
- Admin command (/listpending) to view all users awaiting verification
- Clear messaging for all verification states
- Proper error handling for edge cases

## Setup

### Requirements

- Python 3.7+
- python-telegram-bot library
- Flask

### Environment Variables

The following environment variables need to be set:

- `TELEGRAM_TOKEN`: Your Telegram Bot token from BotFather
- `WEBHOOK_URL` (optional): The public URL where your bot is hosted (not needed for polling mode)
- `USE_POLLING` (optional): Set to "True" to use polling instead of webhooks (better for development)
- `SESSION_SECRET` (optional): Secret key for Flask session (auto-generated if not provided)

### Running the Bot

1. Set the required environment variables
2. Run the Flask application:

