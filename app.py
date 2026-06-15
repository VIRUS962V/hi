from flask import Flask, request, jsonify
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import json

app = Flask(__name__)

# ضع هنا الـ Public Key الخاص بتطبيقك من Discord Developer Portal (وليس الـ Client Secret)
DISCORD_PUBLIC_KEY = "be54d9864c798a0608e7ea3f0822e7213dd83485fb83507768e92f81b370c9b8"

def verify_discord_signature(request):
    """التحقق من أن الطلب قادم فعلاً من Discord لحماية السيرفر"""
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
    # 1. التحقق الأمني
    if not verify_discord_signature(request):
        return jsonify({"error": "Invalid request signature"}), 401

    interaction = request.json
    interaction_type = interaction.get('type')

    # 2. الرد التلقائي على رسالة PING من ديسكورد (Type 1)
    if interaction_type == 1:
        return jsonify({"type": 1})

    # 3. معالجة أوامر الـ Slash Commands (Type 2)
    if interaction_type == 2:
        data = interaction.get('data', {})
        command_name = data.get('name')

        # مثال: إذا كان الأمر هو /post
        if command_name == 'post':
            # يمكنك هنا تخصيص الرسالة أو الروابط التي يتم إرسالها
            embed_content = {
                "title": "إعلان / ترويج جديد",
                "description": "هذه رسالة مرسلة عبر تطبيق خارجي مثبت على الحساب الشخصي.",
                "color": 16711680, # لون أحمر
                "fields": [
                    {"name": "الحالة", "value": "شغال 100%", "inline": True}
                ]
            }
            
            # الرد المباشر الذي سيظهر في القناة
            return jsonify({
                "type": 4, # Channel Message with source
                "data": {
                    "content": "تم نشر الإعلان بنجاح!",
                    "embeds": [embed_content]
                }
            })

        # رد افتراضي للأوامر غير المعروفة
        return jsonify({
            "type": 4,
            "data": {
                "content": "أمر غير معروف."
            }
        })

    return jsonify({"status": "unhandled event"}), 200

if __name__ == '__main__':
    # لتجربة السكربت محلياً، اربطه بـ Ngrok للحصول على رابط HTTPS
    app.run(port=5000, debug=True)
