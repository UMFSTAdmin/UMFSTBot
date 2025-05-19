# UMFST Campus Verification Bot

A Telegram bot for UMFST campus groups that restricts new members until an admin verifies them.

## Features

✅ **Automatic Restriction**: New members are automatically restricted (read-only) when they join
✅ **Welcome Messages**: Bot sends a welcome message to new members with verification instructions
✅ **Admin Notifications**: Sends private messages to admin with verification command instructions
✅ **Verification System**: Admin can verify users with a simple command
✅ **Moderation Tools**: Admin can reject, kick and unban users as needed
✅ **Security**: Helps maintain a secure community of authenticated students

## Admin Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `/verify @username` | `/verify @studentname` | Grants full permissions to a verified user |
| `/reject @username` | `/reject @spamuser` | Removes a user from the group |
| `/unban @username` | `/unban @exuser` | Unbans a user by username so they can rejoin |
| `/unban_id [user_id]` | `/unban_id 1234567890` | Unbans a user by their numeric ID |

## How It Works

1. When a new user joins, they'll be restricted from sending messages
2. The bot sends a welcome message instructing them to verify with an admin
3. Admin receives a notification with the user's information
4. Admin can use `/verify` to approve or `/reject` to remove the user
5. If a user was mistakenly removed, admin can use `/unban` to let them rejoin

## Setup and Usage

1. Install dependencies:
   ```
   pip install python-telegram-bot==22.1
   ```

2. Set the TELEGRAM_TOKEN environment variable:
   ```
   export TELEGRAM_TOKEN=your_bot_token_from_botfather
   ```

3. Run the bot:
   ```
   python telegram_bot.py
   ```

4. Make sure the bot is an admin in your group with appropriate permissions:
   - Can restrict members
   - Can delete messages
   - Can ban users

## Important Notes

- The bot requires the ADMIN_ID set to your Telegram user ID (currently: 7582664657)
- To keep the bot running continuously, consider using a process manager like systemd or a cloud hosting service
- For the `/unban` command to work properly, the user must have a username
- Use `/unban_id` when you need to unban by user ID instead of username

## Troubleshooting

If the bot stops responding or doesn't start:
1. Check that your TELEGRAM_TOKEN is set correctly
2. Ensure the bot has admin permissions in the group
3. Restart the bot using `python telegram_bot.py`

For persistent operation, consider using a process manager or hosting service to keep the bot running 24/7.