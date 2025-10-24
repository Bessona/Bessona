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

# --- Flask для Render ---
@app.route('/')
def home():
    return "Бот работает!"

# --- Получение погоды ---
def get_weather():
    try:
        response = requests.get("https://sinoptik.ua/погода-днепр", timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        city_tag = soup.select_one('.cityName span')
        city = city_tag.text.strip() if city_tag else "Днепр"

        temp_min_tag = soup.select_one('.temperature .min')
        temp_min = temp_min_tag.text.strip() if temp_min_tag else "—"

        temp_max_tag = soup.select_one('.temperature .max')
        temp_max = temp_max_tag.text.strip() if temp_max_tag else "—"

        desc_tag = soup.select_one('.wDescription .description')
        desc = desc_tag.text.strip() if desc_tag else "Описание недоступно"

        return f"🌤 Погода в {city}:\nМин: {temp_min}\nМакс: {temp_max}\n{desc}"
    except Exception as e:
        return f"Ошибка при получении погоды: {e}"

# --- Отправка погоды ---
def send_weather():
    try:
        weather = get_weather()
        bot.send_message(CHAT_ID, weather)
    except Exception as e:
        print("Ошибка при отправке:", e)

# --- Команда /test ---
@bot.message_handler(commands=['test'])
def test(message):
    weather = get_weather()
    bot.send_message(message.chat.id, f"✅ Проверка: бот работает!\n\n{weather}")

# --- Расписание 08:00 ---
def scheduler():
    schedule.every().day.at("08:00").do(send_weather)
    while True:
        schedule.run_pending()
        time.sleep(60)

# --- Запуск бота ---
def run_bot():
    bot.polling(none_stop=True)

# --- Главный запуск ---
if __name__ == "__main__":
    threading.Thread(target=scheduler).start()
    threading.Thread(target=run_bot).start()
    # Flask держит Render активным
    app.run(host="0.0.0.0", port=10000)
