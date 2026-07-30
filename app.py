import os
import subprocess
import sys
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def health():
    return "OK", 200

@app.route('/health')
def health_check():
    return "OK", 200

if __name__ == "__main__":
    # Start bot in background
    import threading
    def run_bot():
        subprocess.run([sys.executable, "bot.py"])
    
    thread = threading.Thread(target=run_bot, daemon=True)
    thread.start()
    
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
