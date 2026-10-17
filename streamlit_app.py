from datetime import datetime, timedelta
import json
import os
import requests
import streamlit as st

# Configurazione della pagina
st.set_page_config(
    page_title="Assistente Domestico", page_icon="💬", layout="centered"
)

st.title("💬 Assistente Domestico")

# Controllo Password
password_inserita = st.text_input("Password d'accesso:", type="password")
if password_inserita != "1234":
  if password_inserita != "":
    st.error("Password errata.")
  st.stop()

# --- GESTIONE STORICO CHAT ---
FILE_STORICO = "chat_history.json"

if "messages" not in st.session_state:
  st.session_state.messages = []
  if os.path.exists(FILE_STORICO):
    try:
      with open(FILE_STORICO, "r", encoding="utf-8") as f:
        st.session_state.messages = json.load(f)
    except Exception:
      pass

  if not st.session_state.messages:
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            "👋 Ciao! Sono il tuo assistente. Posso gestire i report per"
            " Meteo, Ombrellone e Traffico."
        ),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }]


# --- FORMATTAZIONE ORARIO ---
def formatta_orario(timestamp_str):
  if not timestamp_str:
    return ""
  try:
    dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    oggi = datetime.now().date()
    if dt.date() == oggi:
      return dt.strftime("%H:%M")
    elif dt.date() == oggi - timedelta(days=1):
      return f"Ieri {dt.strftime('%H:%M')}"
    else:
      mesi = [
          "gen",
          "feb",
          "mar",
          "apr",
          "mag",
          "giu",
          "lug",
          "ago",
          "set",
          "ott",
          "nov",
          "dic",
      ]
      return f"{dt.day:02d} {mesi[dt.month - 1]}, {dt.strftime('%H:%M')}"
  except Exception:
    return ""


# Visualizzazione messaggi
for msg in st.session_state.messages:
  with st.chat_message(msg["role"]):
    st.markdown(msg["content"])
    orario_fmt = formatta_orario(msg.get("timestamp"))
    if orario_fmt:
      st.caption(f"🕒 {orario_fmt}")


# --- FUNZIONE COMUNICAZIONE GITHUB ---
def invia_dispatch_github(repo_name, event_type):
  # Recupera il token ripulito da spazi
  token = ""
  try:
    if "streamlit_token" in st.secrets:
      token = str(st.secrets["streamlit_token"]).strip()
  except Exception:
    pass

  if not token:
    token = os.getenv("streamlit_token", "").strip()

  if not token:
    return False, "⚠️ Token GitHub non trovato nei secrets (`streamlit_token`)."

  url = f"https://api.github.com/repos/vittorioras-max/{repo_name}/dispatches"

  # Usa Bearer per i token moderni o classici compatibili
  headers = {
      "Authorization": f"Bearer {token}",
      "Accept": "application/vnd.github+json",
  }
  payload = {"event_type": event_type}

  try:
    response = requests.post(url, headers=headers, json=payload, timeout=5)
    if response.status_code == 204:
      return True, f"📡 **Richiesta inviata al repository `{repo_name}`!**"
    else:
      return (
          False,
          f"❌ Errore GitHub ({response.status_code}): {response.text}",
      )
  except Exception as e:
    return False, f"❌ Errore di connessione: {e}"


# --- AZIONI SPECIFICHE ---
def richiedi_meteo():
  ok, msg = invia_dispatch_github(
      repo_name="meteo", event_type="richiedi_meteo"
  )
  if ok:
    return (
        "📊 **Richiesta meteo inoltrata!**\n\nIl workflow sul repository"
        " `meteo` è in esecuzione."
    )
  return msg


def richiedi_meteo_ombrellone():
  ok, msg = invia_dispatch_github(
      repo_name="Ombrellone-meteo", event_type="check_weather"
  )
  if ok:
    return (
        "🌪️ **Richiesta controllo ombrellone inoltrata!**\n\nIl workflow sul"
        " repository `Ombrellone-meteo` è stato avviato."
    )
  return msg


def richiedi_traffico():
  ok, msg = invia_dispatch_github(
      repo_name="Traffic-cl", event_type="richiedi_traffico"
  )
  if ok:
    return (
        "🚗 **Richiesta report traffico inoltrata!**\n\nIl workflow sul"
        " repository `Traffic-cl` è in esecuzione."
    )
  return msg


# --- INTERFACCIA CHAT ---
if prompt := st.chat_input("Chiedi del meteo, dell'ombrellone o del traffico..."):
  ora_attuale = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  st.session_state.messages.append({
      "role": "user",
      "content": prompt,
      "timestamp": ora_attuale,
  })
  with st.chat_message("user"):
    st.markdown(prompt)
    st.caption(f"🕒 {formatta_orario(ora_attuale)}")

  prompt_low = prompt.lower()

  if any(
      k in prompt_low
      for k in ["meteo", "previsioni", "temperatura", "caldo", "freddo", "gradi"]
  ):
    risposta = richiedi_meteo()
  elif any(
      k in prompt_low
      for k in ["ombrello", "ombrellone", "vento", "tempesta", "raffiche"]
  ):
    risposta = richiedi_meteo_ombrellone()
  elif any(
      k in prompt_low
      for k in ["traffico", "calenzano", "strada", "viabilità", "auto"]
  ):
    risposta = richiedi_traffico()
  else:
    risposta = (
        f"Ho ricevuto: '{prompt}'. Puoi chiedermi informazioni sul **meteo**,"
        " sullo **stato dell'ombrellone (vento)** o sul **traffico per"
        " Calenzano**."
    )

  st.session_state.messages.append({
      "role": "assistant",
      "content": risposta,
      "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
  })
  with st.chat_message("assistant"):
    st.markdown(risposta)
    st.caption(f"🕒 {formatta_orario(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}")

  with open(FILE_STORICO, "w", encoding="utf-8") as f:
    json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
      
