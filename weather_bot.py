from flask import Flask
import threading
import requests
from bs4 import BeautifulSoup
import telebot
import schedule
import time

# === Настройки ===
TOKEN = "8261592064:AAFLThqLcAnSBdlSWWon1596-X_zByVo9rY"
CHAT_ID = -1002548699204

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Бот работает на Render!"

def get_weather():
    try:
        # Используем другой сайт с прогнозом, стабильный источник
        url = "https://wttr.in/Dnipro?format=%C+%t+%w"
        response = requests.get(url, timeout=10)
        weather = response.text.strip()
        return f"🌤 Погода в Днепре:\n{weather}"
    except Exception as e:
        return f"Ошибка при получении погоды: {e}"

def send_weather():
    try:
        weather = get_weather()
        bot.send_message(CHAT_ID, weather)
    except Exception as e:
        print("Ошибка при отправке:", e)

@bot.message_handler(commands=['test'])
def test(message):
    send_weather()

def scheduler():
    schedule.every().day.at("08:00").do(send_weather)
    while True:
        schedule.run_pending()
        time.sleep(60)

def run_bot():
    bot.polling(non_stop=True, interval=0, timeout=20)

if __name__ == "__main__":
    threading.Thread(target=scheduler, daemon=True).start()
    threading.Thread(target=run_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
