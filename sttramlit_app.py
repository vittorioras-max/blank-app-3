import streamlit as st

# 1. Configurazione della pagina
st.set_page_config(page_title="Assistente di Famiglia", page_icon="🤖", layout="centered")

# 2. Controllo di accesso tramite password
st.title("🤖 Assistente di Famiglia")
password_inserita = st.text_input("Inserisci la password di accesso:", type="password")

# Sostituisci '1234' con la password che preferisci usare
if password_inserita != "1234":
    if password_inserita != "":
        st.error("Password errata.")
    st.stop()

st.success("Accesso consentito!")

# 3. Gestione della cronologia dei messaggi nella chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostra la cronologia precedente
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Input della chat in basso
if prompt := st.chat_input("Scrivi qui la tua richiesta..."):
    # Salva e mostra il messaggio dell'utente
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Risposta di test iniziale
    risposta = f"Ho ricevuto la tua richiesta: '{prompt}'. L'app di base è attiva e funzionante!"

    # Salva e mostra la risposta dell'assistente
    st.session_state.messages.append({"role": "assistant", "content": risposta})
    with st.chat_message("assistant"):
        st.markdown(risposta)
        
