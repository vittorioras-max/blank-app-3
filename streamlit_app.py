import streamlit as st
import requests
from datetime import datetime, timedelta

# Configurazione pagina stile chat
st.set_page_config(page_title="Assistente Domestico", page_icon="💬", layout="centered")

st.title("💬 Assistente Domestico")

# Controllo Password
password_inserita = st.text_input("Password d'accesso:", type="password")
if password_inserita != "1234":
    if password_inserita != "":
        st.error("Password errata.")
    st.stop()

# Inizializzazione cronologia chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 Ciao! Sono il tuo assistente. Monitoro la sicurezza dell'ombrellone e il traffico per Calenzano."}
    ]

# Visualizzazione messaggi stile Telegram
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- FUNZIONI FOCALIZZATE ---

def controlla_ombrellone():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=43.9333&longitude=10.9167&current=wind_speed_10m,temperature_2m"
        res = requests.get(url, timeout=5).json()
        vento = res["current"]["wind_speed_10m"]
        temp = res["current"]["temperature_2m"]
        
        # Soglia di sicurezza vento (15-20 km/h)
        if vento >= 15:
            return f"🚨 **ALLERTA VENTO ({vento} km/h)**\n\n⚠️ Vento forte rilevato! **Chiudi subito l'ombrellone.**\n(Temperatura attuale: {temp}°C)"
        else:
            return f"🟢 **METEO SICURO ({vento} km/h)**\n\
