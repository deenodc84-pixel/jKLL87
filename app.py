import os
import threading
import time
from flask import Flask, jsonify
from bot import run_bot

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

def run_bot_with_retry():
    """Run the Telegram bot with retry logic"""
    while True:
        try:
            print("🚀 Starting Telegram bot...")
            run_bot()
        except Exception as e:
            print(f"❌ Bot crashed: {e}")
            print("🔄 Restarting bot in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    # Start the bot in a background thread
    bot_thread = threading.Thread(target=run_bot_with_retry, daemon=True)
    bot_thread.start()
    
    # Run Flask server for healthchecks
    port = int(os.environ.get('PORT', 8080))
    print(f"🌐 Starting Flask healthcheck server on port {port}")
    app.run(host='0.0.0.0', port=port)
