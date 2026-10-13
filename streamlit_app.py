import streamlit as st
import requests
import json
import os
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

# --- GESTIONE STORICO CHAT DA FILE JSON ---
FILE_STORICO = "chat_history.json"

if "messages" not in st.session_state:
    st.session_state.messages = []
    # Prova a leggere lo storico dal file se esiste
    if os.path.exists(FILE_STORICO):
        try:
            with open(FILE_STORICO, "r", encoding="utf-8") as f:
                st.session_state.messages = json.load(f)
        except Exception:
            pass
            
    # Se il file non esiste o è vuoto, inserisce il messaggio di benvenuto predefinito
    if not st.session_state.messages:
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
        
    return f"🚗 REPORT TRAFFICO ({destinazione}) - Ore {ora_italiana.strftime('%H:%M')}: Viabilità monitorata per il percorso."

# --- CHAT INTERATTIVA ---

if prompt := st.chat_input("Chiedi del vento, dell'ombrellone o del traffico..."):
    # Salva e mostra messaggio utente
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    prompt_low = prompt.lower()

    if any(k in prompt_low for k in ["vento", "ombrello", "ombrellone", "meteo", "tempesta", "radar", "fulmini", "pioggia", "neve", "temperatura", "caldo", "freddo", "gradi"]):
        risposta = controlla_ombrellone()
    elif any(k in prompt_low for k in ["traffico", "calenzano", "strada", "viabilità", "auto"]):
        risposta = controlla_traffico()
    else:
        risposta = f"Ho ricevuto: '{prompt}'. Puoi chiedermi informazioni sullo **stato dell'ombrellone (vento)** o sul **traffico per Calenzano**."

    # Salva e mostra risposta assistente
    st.session_state.messages.append({"role": "assistant", "content": risposta})
    with st.chat_message("assistant"):
        st.markdown(risposta)
        
    # (Facoltativo per ora): Salvataggio locale dei messaggi interattivi
    with open(FILE_STORICO, "w", encoding="utf-8") as f:
        json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
        
