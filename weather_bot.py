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
    return "✅ Бот работает и готов присылать прогноз!"

def get_weather():
    try:
        url = "https://sinoptik.ua/погода-днепр"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")

        # Город
        city_tag = soup.select_one('.topCity__name') or soup.select_one('.cityName span')
        city = city_tag.get_text(strip=True) if city_tag else "Днепр"

        # Температуры
        temp_min_tag = soup.select_one('.temperature .min') or soup.select_one('.temperature__min')
        temp_max_tag = soup.select_one('.temperature .max') or soup.select_one('.temperature__max')
        temp_min = temp_min_tag.get_text(strip=True) if temp_min_tag else "—"
        temp_max = temp_max_tag.get_text(strip=True) if temp_max_tag else "—"

        # Описание погоды
        desc_tag = soup.select_one('.description') or soup.select_one('.wDescription')
        description = desc_tag.get_text(strip=True) if desc_tag else "Описание недоступно"

        return f"🌤 Погода в {city}:\nМин: {temp_min}\nМакс: {temp_max}\n{description}"

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
    bot.polling(none_stop=True)

if __name__ == "__main__":
    threading.Thread(target=scheduler).start()
    threading.Thread(target=run_bot).start()
    app.run(host="0.0.0.0", port=10000)
