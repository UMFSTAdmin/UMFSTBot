from flask import Flask
import os

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", os.urandom(24).hex())

# Bot configuration
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ADMIN_ID = 7582664657  # Telegram ID of @UMFST_Admin

@app.route('/')
def index():
    """Status page showing bot information"""
    status_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>UMFST Campus Verification Bot</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body data-bs-theme="dark">
        <div class="container mt-5">
            <div class="row justify-content-center">
                <div class="col-md-8">
                    <div class="card">
                        <div class="card-header">
                            <h3>UMFST Campus Verification Bot</h3>
                        </div>
                        <div class="card-body">
                            <p><strong>Status:</strong> Ready</p>
                            <p><strong>Bot Mode:</strong> Polling</p>
                            <p><strong>Admin ID:</strong> """ + str(ADMIN_ID) + """</p>
                            <p class="mt-4">
                                This bot restricts new members in UMFST campus Telegram groups until they're verified
                                by providing their student ID or enrollment proof to an admin.
                            </p>
                            <div class="mt-4">
                                <h5>Features:</h5>
                                <ul>
                                    <li>Automatically restricts new members when they join</li>
                                    <li>Notifies admin about new members requiring verification</li>
                                    <li>Admin can verify or reject members with simple commands</li>
                                    <li>Helps maintain a secure community of actual students</li>
                                </ul>
                            </div>
                            <div class="mt-4">
                                <h5>Commands:</h5>
                                <ul>
                                    <li><code>/verify @username</code> - Grant permissions to a verified user</li>
                                    <li><code>/reject @username</code> - Remove a user from the group</li>
                                </ul>
                            </div>
                            <div class="alert alert-info mt-4">
                                <strong>Note:</strong> When you want to start the bot, run the following steps:
                                <ol>
                                    <li>Install python-telegram-bot v22.1: <code>pip install "python-telegram-bot==22.1"</code></li>
                                    <li>Copy main.py content from your original code</li>
                                    <li>Run the bot using: <code>python main.py</code></li>
                                </ol>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return status_html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)