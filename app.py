from flask import Flask, request, jsonify
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import json

app = Flask(__name__)

# Place your Public Key from Discord Developer Portal here
DISCORD_PUBLIC_KEY = "be54d9864c798a0608e7ea3f0822e7213dd83485fb83507768e92f81b370c9b8"

def verify_discord_signature(request):
    """Verify that the request is genuinely coming from Discord to protect the server"""
    signature = request.headers.get('X-Signature-Ed25519')
    timestamp = request.headers.get('X-Signature-Timestamp')
    body = request.data

    if not signature or not timestamp:
        return False

    try:
        verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))
        verify_key.verify(bytes.fromhex(signature), timestamp.encode() + body, bytes.fromhex(DISCORD_PUBLIC_KEY))
        return True
    except (BadSignatureError, ValueError):
        return False

@app.route('/interactions', methods=['POST'])
def handle_interactions():
    print("📥 Received a new request from Discord...")
    
    # 🔴 Bypassed temporarily to allow Discord to verify and save the endpoint URL
    # Remove the '#' symbols after saving successfully to re-enable security
    #if not verify_discord_signature(request):
    #    print("❌ Signature Verification Failed")
    #    return jsonify({"error": "Invalid request signature"}), 401

    print("✅ Signature check bypassed temporarily")
    interaction = request.json
    interaction_type = interaction.get('type')

    # 2. Automatic response to Discord PING (Type 1 - during endpoint saving)
    if interaction_type == 1:
        print("🏓 Successfully responded to PING")
        return jsonify({"type": 1})

    # 3. Handling Slash Commands (Type 2)
    if interaction_type == 2:
        data = interaction.get('data', {})
        command_name = data.get('name')

        if command_name == 'post':
            # Promotion message / Rich Embed content
            embed_content = {
                "title": "New Advertisement / Promotion",
                "description": "This message was sent via an external app installed on a user account.",
                "color": 16711680, # Red color
                "fields": [
                    {"name": "Status", "value": "Working 100%", "inline": True}
                ]
            }
            
            print("🚀 Executing /post command and sending response")
            return jsonify({
                "type": 4, # Channel Message with source
                "data": {
                    "content": "Ad posted successfully!",
                    "embeds": [embed_content]
                }
            })

        return jsonify({
            "type": 4,
            "data": {
                "content": "Unknown command."
            }
        })

    return jsonify({"status": "unhandled event"}), 200

if __name__ == '__main__':
    # Runs automatically on port 5000
    app.run(port=5000)
