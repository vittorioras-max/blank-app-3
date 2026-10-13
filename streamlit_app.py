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
            return f"🚨 ALLERTA VENTO ({vento} km/h) - Vento forte! Chiudi subito l'ombrellone. (Temp: {temp}°C)"
        else:
            return f"🟢 METEO SICURO ({vento} km/h) - Vento sotto la soglia. L'ombrellone può rimanere aperto. (Temp: {temp}°C)"
    except Exception:
        return "❌ Errore nel recupero dati meteo."

def controlla_traffico():
    ora_italiana = datetime.utcnow() + timedelta(hours=2)
    ora = ora_italiana.hour
    
    if ora < 14:
        destinazione = "Calenzano (Andata lavoro)"
    else:
        destinazione = "Rientro a Casa"
        
    return f"🚗 REPORT TRAFFICO ({destinazione}) - Ore {ora_italiana.strftime('%H:%M')}\n\n
    
