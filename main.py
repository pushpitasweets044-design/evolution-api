import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- Configuration (Render ki Environment Variables se aayenge) ---
HF_TOKEN = os.getenv("HF_TOKEN")
HF_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
EVO_URL = os.getenv("EVO_URL") 
EVO_KEY = os.getenv("EVO_KEY")
INSTANCE = os.getenv("INSTANCE_NAME", "Pushpita")

@app.route('/webhook', methods=['POST'])
def handle_whatsapp():
    data = request.json
    print("Received Data:", data) # Debugging ke liye

    # Check: Kya ye naya message hai aur aapne khud nahi bheja?
    if data.get('event') == 'messages.upsert' and not data['data']['key']['fromMe']:
        user_msg = data['data']['message'].get('conversation') or \
                   data['data']['message'].get('extendedTextMessage', {}).get('text')
        sender = data['data']['key']['remoteJid']

        if user_msg:
            # 1. Hugging Face se answer mangwana
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            hf_res = requests.post(HF_URL, headers=headers, json={"inputs": user_msg})
            
            try:
                # Hugging Face output format ko handle karna
                bot_reply = hf_res.json()[0]['generated_text']
                # Agar model input repeat kare toh use clean karna
                bot_reply = bot_reply.replace(user_msg, "").strip()
            except:
                bot_reply = "Aapka sawal samajh nahi aaya, dubara puchiye."

            # 2. Evolution API ke zariye WhatsApp par reply bhejna
            requests.post(f"{EVO_URL}/message/sendText/{INSTANCE}", 
                          headers={"apikey": EVO_KEY}, 
                          json={"number": sender, "text": bot_reply})
            
    return "OK", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
