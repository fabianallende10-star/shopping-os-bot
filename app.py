import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

# Variables de entorno
gemini_api_key = os.environ.get("GEMINI_API_KEY")
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_TOKEN")

app = Flask(__name__)

def llamar_gemini(mensaje, modelo):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={gemini_api_key}"
    payload = {"contents": [{"parts": [{"text": f"Actúa como Shopping OS. Responde breve y profesional: {mensaje}"}]}]}
    return requests.post(url, json=payload, timeout=7)

@app.route("/webhook", methods=["POST"])
def webhook():
    mensaje_cliente = request.values.get('Body', '').strip()
    remitente = request.values.get('From', '')
    
    # 1. Avisamos a Twilio que estamos procesando
    tw_response = MessagingResponse()
    tw_response.message("Procesando tu solicitud en Shopping OS...")
    
    # 2. Intentamos con varios modelos
    modelos = ["gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-2.5-flash-lite"]
    respuesta_ia = "Estamos teniendo alta demanda. Intente en un momento."

    for modelo in modelos:
        try:
            print(f"🔗 Intentando con {modelo}...")
            res = llamar_gemini(mensaje_cliente, modelo)
            if res.status_code == 200:
                respuesta_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                break
        except Exception as e:
            print(f"❌ Falló {modelo}: {e}")

    # 3. Enviamos la respuesta real por fuera de la conexión de Twilio
    try:
        client = Client(TWILIO_SID, TWILIO_TOKEN)
        client.messages.create(
            body=f"✨ *Shopping OS*\n\n{respuesta_ia[:1000]}",
            from_=request.values.get('To', ''),
            to=remitente
        )
    except Exception as e:
        print(f"❌ Error al enviar mensaje por Twilio: {e}")
    
    return str(tw_response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
