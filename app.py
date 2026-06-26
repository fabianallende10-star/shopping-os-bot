import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# Leemos las variables
gemini_api_key = os.environ.get("GEMINI_API_KEY")

app = Flask(__name__)

def llamar_gemini(mensaje, modelo):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={gemini_api_key}"
    payload = {"contents": [{"parts": [{"text": f"Actúa como Shopping OS. Responde formal y profesional: {mensaje}"}]}]}
    return requests.post(url, json=payload, timeout=8)

@app.route("/webhook", methods=["POST"])
def webhook():
    mensaje_cliente = request.values.get('Body', '').strip()
    
    # Lista de modelos de respaldo (ordenada de mejor a peor)
    modelos = [
        "gemini-3.5-flash",
        "gemini-3.1-flash-lite",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash-lite"
    ]
    
    respuesta_ia = "Estamos teniendo alta demanda en los servidores. Por favor, intente de nuevo en un momento."

    for modelo in modelos:
        try:
            print(f"🔗 Intentando con {modelo}...")
            res = llamar_gemini(mensaje_cliente, modelo)
            if res.status_code == 200:
                respuesta_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                print(f"✅ Éxito con {modelo}")
                break 
            else:
                print(f"⚠️ Falló {modelo}: {res.status_code}")
        except Exception as e:
            print(f"❌ Error crítico con {modelo}: {e}")

    tw_response = MessagingResponse()
    tw_response.message(f"✨ *Shopping OS*\n\n{respuesta_ia}")
    return str(tw_response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
