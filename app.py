import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

# ========================================================
# 🔒 CREDENCIALES SEGURAS (Se configuran en Render)
# ========================================================
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_TOKEN")
gemini_api_key = os.environ.get("GEMINI_API_KEY")

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    mensaje_cliente = request.values.get('Body', '').strip()
    remitente = request.values.get('From', '')
    
    print(f"📩 Mensaje recibido de {remitente}: '{mensaje_cliente}'")
    
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"
    
    prompt_interactivo = (
        "Actúas como el asistente ejecutivo de Inteligencia Artificial de la plataforma premium 'Shopping OS'. "
        "Un cliente te acaba de escribir un mensaje por WhatsApp. Tu deber es responderle de manera "
        "estrictamente profesional, formal, cordial, amigable y muy atenta. "
        "Ayúdale de forma concisa y ejecutiva con sus dudas sobre productos, sugerencias de despensa o el estatus de su cuenta. "
        "Utiliza un formato limpio y recuerda no usar modismos, lenguaje coloquial ni palabras altisonantes.\n\n"
        f"Mensaje del cliente: {mensaje_cliente}"
    )
    
    try:
        gemini_res = requests.post(gemini_url, json={"contents": [{"parts": [{"text": prompt_interactivo}]}]}).json()
        respuesta_ia = gemini_res['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        respuesta_ia = "Estimado cliente, agradecemos su comunicación. En este momento estamos optimizando nuestros sistemas, por lo que le brindaremos una respuesta detallada a la brevedad."

    tw_response = MessagingResponse()
    tw_response.message(f"✨ *Shopping OS* \n\n{respuesta_ia}")
    return str(tw_response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)