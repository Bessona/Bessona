from flask import Flask
import threading
import requests
from bs4 import BeautifulSoup
import telebot
import schedule
import time
import os

# === Настройки ===
TOKEN = "8261592064:AAFLThqLcAnSBdlSWWon1596-X_zByVo9rY"
CHAT_ID = -1002548699204

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Бот работает и готов присылать прогноз!"

# Получение погоды с сайта sinoptik
def get_weather():
    try:
        url = "https://sinoptik.ua/погода-днепр"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")

        city_tag = soup.select_one('.cityName span')
        temp_min_tag = soup.select_one('.temperature .min')
        temp_max_tag = soup.select_one('.temperature .max')
        desc_tag = soup.select_one('.wDescription .description')

        city = city_tag.text.strip() if city_tag else "Днепр"
        temp_min = temp_min_tag.text.strip() if temp_min_tag else "—"
        temp_max = temp_max_tag.text.strip() if temp_max_tag else "—"
        desc = desc_tag.text.strip() if desc_tag else "Описание недоступно"

        return f"🌤 Погода в {city}:\nМин: {temp_min}\nМакс: {temp_max}\n{desc}"
    except Exception as e:
        return f"Ошибка при получении погоды: {e}"

# Отправка прогноза в Telegram
def send_weather():
    try:
        weather = get_weather()
        bot.send_message(CHAT_ID, weather)
    except Exception as e:
        print("Ошибка при отправке:", e)

# Команда /test
@bot.message_handler(commands=['test'])
def test(message):
    send_weather()

# Планировщик на каждый день в 08:00
def scheduler():
    schedule.every().day.at("08:00").do(send_weather)
    while True:
        schedule.run_pending()
        time.sleep(60)

# Запуск polling бота
def run_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    # Стартуем scheduler и polling в отдельных потоках
    threading.Thread(target=scheduler, daemon=True).start()
    threading.Thread(target=run_bot, daemon=True).start()

    # Берём порт Render
    PORT = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=PORT)
