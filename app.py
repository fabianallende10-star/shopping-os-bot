import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# Leemos las variables de entorno
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_TOKEN")
gemini_api_key = os.environ.get("GEMINI_API_KEY")

# DEBUG: Esto imprimirá en los logs de Render si las variables se cargaron bien
print(f"--- DEBUG: SID cargado? {bool(TWILIO_SID)} ---")
print(f"--- DEBUG: TOKEN cargado? {bool(TWILIO_TOKEN)} ---")
print(f"--- DEBUG: GEMINI cargado? {bool(gemini_api_key)} ---")

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    # Obtener el mensaje y quien lo envía
    mensaje_cliente = request.values.get('Body', '').strip()
    remitente = request.values.get('From', '')
    
    print(f"📩 Mensaje recibido de {remitente}: '{mensaje_cliente}'")
    
    # URL de la API de Gemini
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"
    
    prompt_interactivo = (
        "Actúas como el asistente ejecutivo de Inteligencia Artificial de 'Shopping OS'. "
        "Responde de manera profesional, formal, cordial y atenta. "
        "Ayuda al cliente con sus dudas sobre productos, despensa o estatus de cuenta. "
        "No uses modismos, lenguaje coloquial ni palabras altisonantes.\n\n"
        f"Mensaje del cliente: {mensaje_cliente}"
    )
    
    try:
        # Llamada a Gemini
        payload = {"contents": [{"parts": [{"text": prompt_interactivo}]}]}
        gemini_res = requests.post(gemini_url, json=payload).json()
        
        # Extraer respuesta
        respuesta_ia = gemini_res['candidates'][0]['content']['parts'][0]['text']
        print(f"🤖 Respuesta generada: {respuesta_ia}")
        
    except Exception as e:
        print(f"❌ Error al conectar con Gemini: {e}")
        respuesta_ia = "Estimado cliente, agradecemos su comunicación. Estamos optimizando nuestros servicios y le atenderemos en breve."

    # Responder vía Twilio
    tw_response = MessagingResponse()
    tw_response.message(f"✨ *Shopping OS*\n\n{respuesta_ia}")
    return str(tw_response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
