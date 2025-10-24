import telebot
import requests
import schedule
import time
import threading
from flask import Flask
import os

# --- TELEGRAM TOKEN ---
TOKEN = "8261592064:AAFLThqLcAnSBdlSWWon1596-X_zByVo9rY"
bot = telebot.TeleBot(TOKEN)

# --- FLASK SERVER ДЛЯ RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# --- ФУНКЦИЯ ПОЛУЧЕНИЯ ПОГОДЫ ---
def get_weather():
    url = "https://sinoptik.ua/погода-днепр"
    response = requests.get(url)
    if response.status_code == 200:
        text = response.text
        try:
            start = text.find('<div class="today-temp">') + len('<div class="today-temp">')
            end = text.find('</div>', start)
            temp = text[start:end].strip()
            return f"Погода в Днепре сегодня: {temp}"
        except:
            return "Не удалось получить погоду 😔"
    else:
        return "Ошибка при получении данных с сайта."

# --- ОТПРАВКА СООБЩЕНИЯ ---
def send_weather():
    chat_id = -1002548699204
    weather = get_weather()
    bot.send_message(chat_id, weather)

# --- КОМАНДА /start ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Бот запущен и будет присылать погоду каждый день в 8:00 ☀️")

# --- КОМАНДА /test ---
@bot.message_handler(commands=['test'])
def test(message):
    bot.reply_to(message, get_weather())

# --- РАСПИСАНИЕ ---
def schedule_checker():
    schedule.every().day.at("08:00").do(send_weather)
    while True:
        schedule.run_pending()
        time.sleep(30)

# --- ЗАПУСК ПОТОКОВ ---
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    threading.Thread(target=schedule_checker).start()
    print("Bot is running...")
    bot.infinity_polling()
