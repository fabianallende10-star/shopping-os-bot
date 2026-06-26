import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# Leemos las variables desde Render
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_TOKEN")
gemini_api_key = os.environ.get("GEMINI_API_KEY")

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    # Obtener el mensaje enviado por el cliente
    mensaje_cliente = request.values.get('Body', '').strip()
    print(f"📩 Mensaje recibido: '{mensaje_cliente}'")
    
    # URL con el modelo 'gemini-2.5-flash-lite' (más estable)
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={gemini_api_key}"
    
    try:
        # Preparar el prompt para Gemini
        payload = {
            "contents": [{
                "parts": [{"text": f"Actúa como el asistente de Shopping OS. Responde formal, profesional y atento a: {mensaje_cliente}"}]
            }]
        }
        
        print("🔗 Intentando conectar con Gemini 2.5 Flash Lite...")
        gemini_res = requests.post(gemini_url, json=payload, timeout=10)
        
        # Verificar respuesta
        if gemini_res.status_code == 200:
            datos = gemini_res.json()
            respuesta_ia = datos['candidates'][0]['content']['parts'][0]['text']
        else:
            print(f"⚠️ Error de API Gemini (Status {gemini_res.status_code}): {gemini_res.text}")
            respuesta_ia = "Disculpe, estamos realizando ajustes técnicos. Le atenderemos en un momento."
            
    except Exception as e:
        print(f"❌ ERROR CRÍTICO EN EL CÓDIGO: {e}")
        respuesta_ia = "Estamos trabajando en la mejora de nuestros sistemas, disculpe la molestia."

    # Responder vía Twilio
    tw_response = MessagingResponse()
    tw_response.message(f"✨ *Shopping OS*\n\n{respuesta_ia}")
    return str(tw_response)

if __name__ == "__main__":
    # Render asigna el puerto mediante la variable PORT
    port = int(os.environ.get("PORT", 10000)) 
    app.run(host="0.0.0.0", port=port)
