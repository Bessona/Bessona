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
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, "html.parser")

        # Безопасно достаём данные
        city = soup.select_one('.cityName span')
        temp_min = soup.select_one('.temperature .min')
        temp_max = soup.select_one('.temperature .max')
        desc = soup.select_one('.description')

        city = city.text.strip() if city else "Днепр"
        temp_min = temp_min.text.strip() if temp_min else "—"
        temp_max = temp_max.text.strip() if temp_max else "—"
        desc = desc.text.strip() if desc else "Описание недоступно"

        return f"🌤 Погода в {city}:\nМин: {temp_min}\nМакс: {temp_max}\n{desc}"
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
