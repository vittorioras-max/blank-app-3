from collections import defaultdict
from datetime import datetime, timedelta
import os
import requests
import base64
import json

# 1. Recupero credenziali dai Secrets di GitHub
TOMTOM_API_KEY = os.environ.get("TOMTOM_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
GITHUB_TOKEN = os.environ.get(
    "STREAMLIT_TOKEN"
)  # Token con permessi di scrittura su blank-app-3


# 2. Funzione per aggiornare la chat in blank-app-3 (uguale a quella del meteo)
def aggiorna_chat_blank_app(testo_messaggio):
  owner = "vittorioras-max"
  repo = "blank-app-3"
  path = "chat_history.json"

  headers = {
      "Authorization": f"token {GITHUB_TOKEN}",
      "Accept": "application/vnd.github.v3+json",
  }

  url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

  try:
    response = requests.get(url, headers=headers)
    storico = []
    sha = None

    if response.status_code == 200:
      file_data = response.json()
      sha = file_data["sha"]
      decoded_content = base64.b64decode(file_data["content"]).decode("utf-8")
      storico = json.loads(decoded_content)

    # Aggiunge il nuovo messaggio alla cronologia
    storico.append({
        "role": "assistant",
        "content": testo_messaggio,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })

    nuovo_contenuto_str = json.dumps(storico, ensure_ascii=False, indent=4)
    nuovo_contenuto_b64 = base64.b64encode(
        nuovo_contenuto_str.encode("utf-8")
    ).decode("utf-8")

    payload = {
        "message": "Aggiornamento automatico traffico [skip ci]",
        "content": nuovo_contenuto_b64,
        "sha": sha,
    }

    put_res = requests.put(url, headers=headers, json=payload, timeout=10)
    if put_res.status_code in [200, 201]:
      print("💬 Chat di blank-app-3 aggiornata con successo!")
    else:
      print(
          f"⚠️ Errore scrittura chat (HTTP {put_res.status_code}):"
          f" {put_res.text}"
      )

  except Exception as e:
    print(f"⚠️ Errore aggiornamento chat blank-app-3: {e}")


# 3. Logica di calcolo del traffico con TomTom
ora_italiana = datetime.utcnow() + timedelta(hours=2)
ora = ora_italiana.hour

# Selezione coordinate in base all'orario (andata o ritorno)
if ora < 14:
  destinazione = "Calenzano (Andata lavoro)"
  origine_lat, origine_lon = 43.7855, 10.863  # Casa (esempio)
  dest_lat, dest_lon = 43.8407, 11.167  # Lavoro (esempio)
else:
  destinazione = "Rientro a Casa"
  origine_lat, origine_lon = 43.8407, 11.167
  dest_lat, dest_lon = 43.7855, 10.863

url_tomtom = (
    f"https://api.tomtom.com/routing/1/calculateRoute/{origine_lat},{origine_lon}:{dest_lat},{dest_lon}/json?"
    f"key={TOMTOM_API_KEY}&traffic=true"
)

try:
  res = requests.get(url_tomtom, timeout=10)
  dati = res.json()

  route = dati["routes"][0]["summary"]
  tempo_impiegato = round(route["travelTimeInSeconds"] / 60)
  traffico_ritardo = round(route.get("trafficDelayInSeconds", 0) / 60)

  messaggio_finale = (
      f"🚗 *REPORT TRAFFICO* ({destinazione}) - Ore"
      f" {ora_italiana.strftime('%H:%M')}:\n\n- Tempo stimato: *"
      f"{tempo_impiegato} min*\n- Ritardo per traffico: *"
      f"{traffico_ritardo} min*"
  )

  # 4. Invio su Telegram
  url_tg = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload_tg = {
      "chat_id": TELEGRAM_CHAT_ID,
      "text": messaggio_finale,
      "parse_mode": "Markdown",
  }

  res_tg = requests.post(url_tg, data=payload_tg, timeout=10)
  if res_tg.status_code == 200:
    print("🚗 Report traffico inviato con successo su Telegram!")
  else:
    print(f"❌ Errore invio Telegram (HTTP {res_tg.status_code}):", res_tg.text)

  # 5. Aggiorna la app Streamlit (blank-app-3)
  aggiorna_chat_blank_app(messaggio_finale)

except Exception as e:
  print(f"❌ Errore nel calcolo del traffico o aggiornamento chat: {e}")
  raise e
    
