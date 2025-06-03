import openmeteo_requests
import pandas as pd
import requests
import requests_cache
from retry_requests import retry
import time
import re

# === Bot Configuration ===
TOKEN = "7525009624:AAFu8ZFx0ft9PE2pt06vHOjBtOdq-_1s81s"
CHAT_ID = "7064542354"
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

# === Send Telegram Message ===
def send_telegram_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    payload = {'chat_id': chat_id, 'text': text}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("✅ Telegram message sent successfully!")
    else:
        print(f"❌ Failed to send message: {response.status_code} {response.text}")

# === Fetch Telegram Updates ===
def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {'timeout': 100, 'offset': offset}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get updates: {response.status_code} {response.text}")
        return None

# === Handle Bot Commands ===
def handle_commands(updates, started_flag, interval_sec):
    last_update_id = None
    for update in updates.get("result", []):
        last_update_id = update["update_id"]
        if "message" in update and "text" in update["message"]:
            chat_id = update["message"]["chat"]["id"]
            text = update["message"]["text"].strip().lower()
            print(f"Received message: {text} from chat {chat_id}")

            if text == "/start":
                send_telegram_message(chat_id, "✅ Weather bot started sending updates!")
                started_flag[0] = True

            elif text == "/stop":
                send_telegram_message(chat_id, "🛑 Weather bot stopped sending updates!")
                started_flag[0] = False

            elif text.startswith("/interval"):
                match = re.match(r"/interval\s+(\d+)", text)
                if match:
                    new_interval = int(match.group(1))
                    if new_interval >= 5:
                        interval_sec[0] = new_interval
                        send_telegram_message(chat_id, f"⏱️ Update interval set to {new_interval} seconds.")
                    else:
                        send_telegram_message(chat_id, "⚠️ Please provide an interval of at least 5 seconds.")
                else:
                    send_telegram_message(chat_id, "⚠️ Usage: /interval <seconds> (minimum 5 seconds)")

            elif text == "/help":
                help_msg = (
                    "📘 *Available Commands:*\n"
                    "/start - Start weather updates\n"
                    "/stop - Stop updates\n"
                    "/interval <seconds> - Set update interval (min 5s)\n"
                    "/weather - Show current weather\n"
                    "/help - Show this help message"
                )
                send_telegram_message(chat_id, help_msg)

            elif text == "/weather":
                try:
                    df = fetch_weather()
                    current_time = pd.Timestamp.utcnow()
                    closest = df.iloc[(df["date"] - current_time).abs().argsort()[:1]]
                    temp = closest["temperature_2m"].values[0]
                    timestamp = closest["date_local"].values[0]
                    timestamp_str = pd.to_datetime(timestamp).strftime("%Y-%m-%d %H:%M %Z")
                    message = f"🌤️ Weather Update for Prague\nTime: {timestamp_str}\nTemperature: {temp:.1f}°C"
                    send_telegram_message(chat_id, message)
                except Exception as e:
                    send_telegram_message(chat_id, f"❌ Error fetching weather: {e}")
    return last_update_id

# === Open-Meteo Setup ===
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

params = {
    "latitude": 50.0755,
    "longitude": 14.4378,
    "hourly": "temperature_2m"
}

def fetch_weather():
    responses = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=params)
    response = responses[0]
    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        "temperature_2m": hourly_temperature_2m
    }
    df = pd.DataFrame(hourly_data)
    df["date_local"] = df["date"].dt.tz_convert(response.Timezone())
    return df

# === Main Program Loop ===
def main():
    send_telegram_message(CHAT_ID, "🤖 Weather bot is online. Use /start to begin and /stop to end updates.")
    started = [False]       # Mutable boolean flag
    interval_sec = [10]     # Mutable interval in seconds
    offset = None

    while True:
        updates = get_updates(offset)
        if updates:
            offset = handle_commands(updates, started, interval_sec)
            if offset is not None:
                offset += 1

        if started[0]:
            try:
                df = fetch_weather()
                current_time = pd.Timestamp.utcnow()
                closest = df.iloc[(df["date"] - current_time).abs().argsort()[:1]]
                temp = closest["temperature_2m"].values[0]
                timestamp = closest["date_local"].values[0]
                timestamp_str = pd.to_datetime(timestamp).strftime("%Y-%m-%d %H:%M %Z")
                message = f"🌤️ Weather Update for Prague\nTime: {timestamp_str}\nTemperature: {temp:.1f}°C"
                send_telegram_message(CHAT_ID, message)
            except Exception as e:
                error_msg = f"❌ Error retrieving weather: {e}"
                send_telegram_message(CHAT_ID, error_msg)
                print(error_msg)

        time.sleep(interval_sec[0])

if __name__ == "__main__":
    main()
