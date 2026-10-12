import os
import requests

API_KEY = os.environ.get("API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def invia_notifica_telegram(messaggio):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Token o Chat ID Telegram mancanti nei Secrets!")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": messaggio, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        print("Risposta Telegram:", response.status_code)
    except Exception as e:
        print(f"Errore invio Telegram: {e}")

def analizza_partite_live():
    if not API_KEY:
        print("API_KEY mancante nei Secrets di GitHub!")
        return

    url = "https://api.football-data.org/v4/matches?status=LIVE"
    headers = {"X-Auth-Token": API_KEY}

    response = requests.get(url, headers=headers)
    print(f"Stato chiamata API Calcio: {response.status_code}")

    if response.status_code != 200:
        print(f"Errore risposta API: {response.text}")
        return

    data = response.json()
    matches = data.get("matches", [])

    if not matches:
        print("Nessuna partita live in corso al momento.")
        return

    print(f"Trovate {len(matches)} partite live.")

    for match in matches:
        squadra_casa = match["homeTeam"]["name"]
        squadra_trasferta = match["awayTeam"]["name"]
        
        score = match.get("score", {}).get("fullTime", {})
        gol_casa = score.get("home") if score.get("home") is not None else 0
        gol_trasferta = score.get("away") if score.get("away") is not None else 0
        totale_gol = gol_casa + gol_trasferta

        minuto = match.get("minute", 0) if match.get("minute") is not None else 0

        print(f"Match: {squadra_casa} vs {squadra_trasferta} | Min: {minuto} | Gol: {totale_gol}")

        if 25 <= minuto <= 40 and totale_gol == 0:
            msg = f"🚨 *SEGNALE OVER 0.5*\n⚽ {squadra_casa} vs {squadra_trasferta}\n⏱ {minuto}' | 0-0"
            invia_notifica_telegram(msg)
        elif 60 <= minuto <= 75 and totale_gol == 1:
            msg = f"🚨 *SEGNALE OVER 1.5*\n⚽ {squadra_casa} vs {squadra_trasferta}\n⏱ {minuto}' | {gol_casa}-{gol_trasferta}"
            invia_notifica_telegram(msg)

if __name__ == "__main__":
    analizza_partite_live()
