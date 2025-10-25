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
        # Используем wttr.in с русским языком и форматом JSON
        url = "https://wttr.in/Dnipro?format=j1&lang=ru"
        response = requests.get(url, timeout=10)
        data = response.json()

        # Извлекаем данные
        current = data["current_condition"][0]
        weather_today = data["weather"][0]

        temp = current["temp_C"]
        feels = current["FeelsLikeC"]
        desc = current["lang_ru"][0]["value"].capitalize()
        wind = current["windspeedKmph"]
        humidity = current["humidity"]

        temp_min = weather_today["mintempC"]
        temp_max = weather_today["maxtempC"]

        message = (
            f"🌤 Погода в Днепре сегодня:\n\n"
            f"Температура: {temp}°C (ощущается как {feels}°C)\n"
            f"Минимум: {temp_min}°C, максимум: {temp_max}°C\n"
            f"Ветер: {wind} км/ч\n"
            f"Влажность: {humidity}%\n"
            f"Описание: {desc}"
        )
        return message

    except Exception as e:
        return f"⚠️ Ошибка при получении погоды: {e}"

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
