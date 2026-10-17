from datetime import datetime, timedelta
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
            "👋 Ciao! Sono il tuo assistente. Posso gestire i report per"
            " Meteo, Ombrellone e Traffico."
        ),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }]


# --- FUNZIONE PER FORMATTARE L'ORARIO STILE TELEGRAM/WHATSAPP ---
def formatta_orario(timestamp_str):
  if not timestamp_str:
    return ""
  try:
    dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    oggi = datetime.now().date()
    data_msg = dt.date()

    if data_msg == oggi:
      return dt.strftime("%H:%M")
    elif data_msg == oggi - timedelta(days=1):
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
      mese_txt = mesi[dt.month - 1]
      return f"{dt.day:02d} {mese_txt}, {dt.strftime('%H:%M')}"
  except Exception:
    return ""


# Visualizzazione messaggi stile chat con orario tipo Telegram/WhatsApp
for msg in st.session_state.messages:
  with st.chat_message(msg["role"]):
    st.markdown(msg["content"])
    orario_fmt = formatta_orario(msg.get("timestamp"))
    if orario_fmt:
      st.caption(f"🕒 {orario_fmt}")

# --- FUNZIONE SICURA PER IL TOKEN ---


def get_github_token():
  # Cerca prima il tuo secret esatto 'streamlit_token', poi le varianti
  for nome_chiave in [
      "streamlit_token",
      "STREAMLIT_TOKEN",
      "GITHUB_TOKEN",
      "Streamlit_token",
  ]:
    token = os.getenv(nome_chiave)
    if token:
      return token
    try:
      if nome_chiave in st.secrets:
        return st.secrets[nome_chiave]
    except Exception:
      pass
  return ""


# --- FUNZIONE GENERICA TRIGGER GITHUB ---


def invia_dispatch_github(repo_name, event_type):
  """Invia un evento repository_dispatch al repository GitHub specificato."""
  # .strip() rimuove eventuali spazi o a capo invisibili copiati nei secret
  github_token = get_github_token().strip()

  if not github_token:
    return (
        False,
        "⚠️ Token GitHub non configurato nei secrets dell'app (verifica"
        " `streamlit_token`).",
    )

  url = f"https://api.github.com/repos/vittorioras-max/{repo_name}/dispatches"

  # Sceglie automaticamente lo schema corretto in base al tipo di token
  schema = "Bearer" if github_token.startswith("github_pat_") else "token"

  headers = {
      "Authorization": f"{schema} {github_token}",
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


# --- FUNZIONI COMANDO SPECIFICHE ---


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
        "🚗 **Richiesta report traffico inoltrata!**\n\nIl workflow `Report"
        " Traffico TomTom` su GitHub è in esecuzione."
    )
  return msg


# --- CHAT INTERATTIVA ---

if prompt := st.chat_input("Chiedi del meteo, dell'ombrellone o del traffico..."):
  ora_attuale = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

  # Salvataggio messaggio utente
  st.session_state.messages.append({
      "role": "user",
      "content": prompt,
      "timestamp": ora_attuale,
  })
  with st.chat_message("user"):
    st.markdown(prompt)
    st.caption(f"🕒 {formatta_orario(ora_attuale)}")

  prompt_low = prompt.lower()

  # ROUTER PAROLE CHIAVE
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

  # Salvataggio risposta assistente
  st.session_state.messages.append({
      "role": "assistant",
      "content": risposta,
      "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
  })
  with st.chat_message("assistant"):
    st.markdown(risposta)
    st.caption(f"🕒 {formatta_orario(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}")

  # Salva la cronologia completa su file
  with open(FILE_STORICO, "w", encoding="utf-8") as f:
    json.dump(st.session_state.messages, f, ensure_ascii=False, indent=4)
      
