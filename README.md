# 🌤️ Telegram Weather Bot for Prague

A Python-based Telegram bot that sends live weather updates for Prague using the Open-Meteo API. Built with `requests`, `pandas`, and deployed on Railway.

---

## 🚀 Features

- ✅ Start and stop automatic weather updates with `/start` and `/stop`
- ⏱️ Change update interval using `/interval <seconds>`
- 🌡️ Get instant weather with `/weather`
- 📘 View all commands using `/help`
- 🧠 Fetches accurate hourly temperature data from [Open-Meteo](https://open-meteo.com/)

---

## ⚙️ Technologies Used

- **Python 3**
- **Telegram Bot API**
- **Open-Meteo API**
- `requests`, `pandas`, `openmeteo-requests`, `requests-cache`, `retry-requests`
- ✅ Hosted on [Railway](https://railway.app)

---

## 📦 Installation

```bash
git clone https://github.com/yourusername/weather-bot.git
cd weather-bot
pip install -r requirements.txt
python main.py
