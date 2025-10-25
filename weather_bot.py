from flask import Flask
import threading
import requests
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
    return "✅ Бот работает и готов присылать прогноз!"

def get_weather():
    try:
        url = "https://wttr.in/Dnipro?format=3"
        response = requests.get(url, timeout=10)
        response.encoding = 'utf-8'
        return response.text  # Например: "Dnipro: 🌦 +12°C"
    except Exception as e:
        return f"Ошибка при получении погоды: {e}"

def send_weather():
    try:
        weather = get_weather()
        bot.send_message(CHAT_ID, f"🌤 Погода в Днепре:\n{weather}")
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
    bot.polling(none_stop=True)

if __name__ == "__main__":
    threading.Thread(target=scheduler).start()
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=10000)
