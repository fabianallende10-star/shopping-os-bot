import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

gemini_api_key = os.environ.get("GEMINI_API_KEY")
app = Flask(__name__)

def llamar_gemini(mensaje, modelo):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={gemini_api_key}"
    # Le pedimos explícitamente que sea corto
    payload = {"contents": [{"parts": [{"text": f"Responde como Shopping OS, muy breve y profesional: {mensaje}"}]}]}
    return requests.post(url, json=payload, timeout=8)

@app.route("/webhook", methods=["POST"])
def webhook():
    mensaje_cliente = request.values.get('Body', '').strip()
    modelos = ["gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-2.5-flash-lite"]
    
    respuesta_final = "Estamos procesando su solicitud, por favor espere un momento."

    for modelo in modelos:
        try:
            res = llamar_gemini(mensaje_cliente, modelo)
            if res.status_code == 200:
                # Extraemos y cortamos a 1000 caracteres para no saturar a Twilio
                texto = res.json()['candidates'][0]['content']['parts'][0]['text']
                respuesta_final = texto[:1000] 
                break
        except:
            continue

    tw_response = MessagingResponse()
    tw_response.message(f"✨ *Shopping OS*\n\n{respuesta_final}")
    return str(tw_response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
