import os
import requests
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

app = Flask(__name__)

# Credenciales
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MELI_ID = os.environ.get("MELI_CLIENT_ID")
MELI_SECRET = os.environ.get("MELI_CLIENT_SECRET")
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_TOKEN = os.environ.get("TWILIO_TOKEN")
REDIRECT_URI = "https://shopping-os-bot.onrender.com/callback"
TOKEN_FILE = "token.txt"

# Funciones de persistencia de Mercado Libre
def get_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f: return f.read().strip()
    return None

def save_token(token):
    with open(TOKEN_FILE, "w") as f: f.write(token)

@app.route("/auth")
def auth():
    return redirect(f"https://auth.mercadolibre.com.mx/authorization?response_type=code&client_id={MELI_ID}&redirect_uri={REDIRECT_URI}")

@app.route("/callback")
def callback():
    code = request.args.get("code")
    data = {"grant_type": "authorization_code", "client_id": MELI_ID, "client_secret": MELI_SECRET, "code": code, "redirect_uri": REDIRECT_URI}
    res = requests.post("https://api.mercadolibre.com/oauth/token", data=data)
    token = res.json().get("access_token")
    if token:
        save_token(token)
        return "¡Token guardado permanentemente! Ya puedes cerrar esta ventana."
    return "Error al obtener el token."

def obtener_pedidos():
    token = get_token()
    if not token: return "No conectado a ML."
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get("https://api.mercadolibre.com/orders/search/recent", headers=headers)
    compras = res.json().get("results", [])
    return str([c['items'][0]['title'] for c in compras[:3]])

def llamar_gemini(mensaje, modelo, contexto):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": f"Shopping OS. Contexto compras: {contexto}. Responde profesional: {mensaje}"}]}]}
    return requests.post(url, json=payload, timeout=7)

@app.route("/webhook", methods=["POST"])
def webhook():
    mensaje_cliente = request.values.get('Body', '').strip()
    remitente = request.values.get('From', '')
    
    # Respuesta inmediata para Twilio
    tw_response = MessagingResponse()
    tw_response.message("Procesando en Shopping OS...")
    
    # Contexto de ML
    contexto = ""
    if "compra" in mensaje_cliente.lower() or "pedido" in mensaje_cliente.lower():
        contexto = f"Mis últimas compras son: {obtener_pedidos()}"

    # Lógica de modelos (El respaldo que ya teníamos)
    modelos = ["gemini-3.1-flash-lite", "gemini-3.5-flash"]
    respuesta_ia = "Error técnico, intenta de nuevo."
    for modelo in modelos:
        try:
            res = llamar_gemini(mensaje_cliente, modelo, contexto)
            if res.status_code == 200:
                respuesta_ia = res.json()['candidates'][0]['content']['parts'][0]['text']
                break
        except: continue

    # Envío asíncrono
    try:
        Client(TWILIO_SID, TWILIO_TOKEN).messages.create(body=f"✨ *Shopping OS*\n\n{respuesta_ia[:1000]}", from_=request.values.get('To', ''), to=remitente)
    except: pass
    
    return str(tw_response)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
