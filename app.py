import os
import threading
from flask import Flask, jsonify
from bot import main as bot_main

# Create Flask app for healthchecks
app = Flask(__name__)

@app.route('/')
def health():
    """Health check endpoint for Railway"""
    return jsonify({"status": "healthy", "message": "Word Detective Bot is running!"}), 200

@app.route('/health')
def health_check():
    """Alternative health check endpoint"""
    return jsonify({"status": "ok"}), 200

def run_bot():
    """Run the Telegram bot in a separate thread"""
    bot_main()

if __name__ == "__main__":
    # Start the bot in a background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Run Flask server for healthchecks
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
