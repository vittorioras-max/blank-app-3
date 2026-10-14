from datetime import datetime
import json
import os
import requests
import streamlit as st

# Configurazione pagina stile chat
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

# --- GESTIONE STORICO CHAT DA FILE JSON ---
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
            "👋 Ciao! Sono il tuo assistente. Invio le richieste per il"
            " monitoraggio dell'ombrellone e del traffico ai relativi"
            " repository."
        ),
    }]

# Visualizzazione messaggi stile Telegram
for msg in st.session_state.messages:
  with st.chat_message(msg["role"]):
    st.markdown(msg["content"])

# --- FUNZIONE GENERICA TRIGGER GITHUB ---


def invia_dispatch_github(repo_name, event_type):
  """Invia un evento repository_dispatch al repository GitHub specificato."""
  github_token = (
      os.getenv("STREAMLIT_TOKEN")
      or st.secrets.get("STREAMLIT_TOKEN", "")
      or os.getenv("GITHUB_TOKEN")
      or st.secrets.get("GITHUB_TOKEN", "")
  )

  if not github_token:
    return (
        False,
        "⚠️ Token GitHub non configurato nei secrets dell'app (`GITHUB_TOKEN` o"
        " `STREAMLIT_TOKEN`).",
    )

  url = f"https://api.github.com/repos/vittorioras-max/{repo_name}/dispatches"
  headers = {
      "Authorization": f"Bearer {github_token}",
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
          f"❌ Errore risposta GitHub ({response.status_code}): {response.text}",
      )
  except Exception as e:
    return False, f"❌ Errore di connessione con GitHub: {e}"


# --- FUNZIONI COMANDO ---


def richiedi_meteo_ombrellone():
  # Sostituisci 'NomeRepoMeteo' con il nome esatto del tuo repository meteo/ombrellone
  ok, msg = invia_dispatch_github(
      repo_name="NomeRepoMeteo", event_type="richiedi_meteo"
  )
  if ok:
    return (
        "🌪️ **Richiesta controllo ombrellone inoltrata!**\n\nIl workflow sul"
        " repository meteo è stato avviato e riceverai l'aggiornamento."
    )
  return msg


def richiedi_traffico():
  ok, msg = invia_dispatch_github(
      repo_name="Traffic-cl", event_type="richiedi_traffico"
  )
  if ok:
    return (
        "🚗 **Richiesta report traffico inoltrata!**\n\nIl workflow `Report"
        " Traffico TomTom` su GitHub è in esecuzione."
    )
  return msg


# --- CHAT INTERATTIVA ---

if prompt := st.chat_input("Chiedi del vento, dell'ombrellone o del traffico..."):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
    st.markdown(prompt)

  prompt_low = prompt.lower()

  if any(
      k in prompt_low
      for k in [
          "vento",
          "ombrello",
          "ombrellone",
          "meteo",
          "tempesta",
          "radar",
          "fulmini",
          "pioggia",
          "neve",
          "temperatura",
          "caldo",
          "freddo",
          "gradi",
      ]
  ):
    risposta = richiedi_meteo_ombrellone()
  elif any(
      k in prompt_low
      for k in ["traffico", "calenzano", "strada", "viabilità", "auto"]
  ):
    risposta = richiedi_traffico()
  else:
    risposta = (
        f"Ho ricevuto: '{prompt}'. Puoi chiedermi informazioni sullo **stato"
        " dell'ombrellone (vento)** o sul **traffico per Calenzano**."
    )

  st.session_state.messages.append({"role": "assistant", "content": risposta})
  with st.chat_message("assistant"):
    st.markdown(risposta)

  with open(FILE_STORICO, "w", encoding="utf-8") as f:
    json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
      
