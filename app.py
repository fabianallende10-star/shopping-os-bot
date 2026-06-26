import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# Leemos las variables
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_TOKEN")
gemini_api_key = os.environ.get("GEMINI_API_KEY")

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    mensaje_cliente = request.values.get('Body', '').strip()
    print(f"📩 Mensaje recibido: '{mensaje_cliente}'")
    
    # URL actualizada con el modelo 'gemini-3.5-flash' que SI existe en tu lista
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={gemini_api_key}"
    
    try:
        payload = {
            "contents": [{
                "parts": [{"text": f"Actúa como el asistente de Shopping OS. Responde formal, profesional y atento a: {mensaje_cliente}"}]
            }]
        }
        
        print("🔗 Intentando conectar con Gemini 3.5 Flash...")
        gemini_res = requests.post(gemini_url, json=payload, timeout=10)
        
        if gemini_res.status_code == 200:
            datos = gemini_res.json()
            respuesta_ia = datos['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"⚠️ Error de API Gemini (Status {gemini_res.status_code}): {gemini_res.text}")
            respuesta_ia = "Estamos realizando ajustes, intentaremos atenderle en un momento."
            
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
        respuesta_ia = "Estamos trabajando en la mejora de nuestros sistemas."

    tw_response = MessagingResponse()
    tw_response.message(f"✨ *Shopping OS*\n\n{respuesta_ia}")
    return str(tw_response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000)) 
    app.run(host="0.0.0.0", port=port)
