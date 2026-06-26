import os
import requests
from flask import Flask, request

# Leemos las variables
gemini_api_key = os.environ.get("GEMINI_API_KEY")

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    # URL para listar modelos
    list_url = f"https://generativelanguage.googleapis.com/v1/models?key={gemini_api_key}"
    
    try:
        print("🔍 Consultando modelos disponibles a Google...")
        response = requests.get(list_url)
        print(f"✅ Respuesta de Google: {response.text}")
    except Exception as e:
        print(f"❌ Error al consultar: {e}")
        
    return "Revisa los logs"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
