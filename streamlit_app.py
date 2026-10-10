import streamlit as st
import requests
from datetime import datetime

# 1. Configurazione della pagina
st.set_page_config(page_title="Assistente di Famiglia", page_icon="🤖", layout="centered")

# 2. Controllo di accesso tramite password
st.title("🤖 Assistente di Famiglia")
password_inserita = st.text_input("Inserisci la password di accesso:", type="password")

if password_inserita != "1234":
    if password_inserita != "":
        st.error("Password errata.")
    st.stop()

st.success("Accesso consentito!")

# 3. Gestione della cronologia dei messaggi
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Funzione meteo reale (Open-Meteo)
def ottieni_meteo():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=43.9333&longitude=10.9167&current=wind_speed_10m,temperature_2m"
        res = requests.get(url, timeout=5).json()
        vento = res["current"]["wind_speed_10m"]
        temp = res["current"]["temperature_2m"]
        
        if vento > 20:
            return f"⚠️ **Attenzione Vento!** Velocità vento: **{vento} km/h** (Temperatura: {temp}°C)."
        else:
            return f"🌤️ **Meteo tranquillo**: Vento a **{vento} km/h** e temperatura di **{temp}°C**."
    except Exception:
        return "Non sono riuscito a recuperare i dati meteo."

# 5. Funzione traffico con controllo orario e Calenzano
def ottieni_traffico():
    ora_attuale = datetime.now().hour
    
    # Esempio di gestione basata sull'orario (es. prima delle 14:00 vs dopo le 14:00)
    if ora_attuale < 14:
        destinazione = "Calenzano (Andata)"
        stato_strada = "Scorrevole sulla A1 / viabilità principale."
    else:
        destinazione = "Rientro (verso casa)"
        stato_strada = "Traffico regolare, nessun rallentamento segnalato."
        
    return f"🚗 **Situazione Traffico ({destinazione})** - Ore {datetime.now().strftime('%H:%M')}:\n- {stato_strada}"

# 6. Interazione Chat
if prompt := st.chat_input("Scrivi qui la tua richiesta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    prompt_lower = prompt.lower()
    
    if any(p in prompt_lower for p in ["meteo", "vento", "tempo", "ombrello"]):
        risposta = ottieni_meteo()
    elif any(p in prompt_lower for p in ["traffico", "strada", "viabilità", "auto", "calenzano"]):
        risposta = ottieni_traffico()
    else:
        risposta = f"Ho ricevuto: '{prompt}'. Chiedimi pure del **meteo** o del **traffico**!"

    st.session_state.messages.append({"role": "assistant", "content": risposta})
    with st.chat_message("assistant"):
        st.markdown(risposta)
        
