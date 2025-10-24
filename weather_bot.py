import requests
from bs4 import BeautifulSoup
import telebot
import schedule
import threading
import time

# === Настройки ===
TOKEN = "8261592064:AAFLThqLcAnSBdlSWWon1596-X_zByVo9rY"
CHAT_ID = -1002548699204

bot = telebot.TeleBot(TOKEN)

# === Получение погоды ===
def get_weather():
    try:
        response = requests.get("https://sinoptik.ua/погода-днепр", timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        city_tag = soup.select_one('.cityName span')
        city = city_tag.text.strip() if city_tag else "Днепр"

        date_tag = soup.select_one('.date')
        date = date_tag.text.strip() if date_tag else ""

        month_tag = soup.select_one('.month')
        month = month_tag.text.strip() if month_tag else ""

        temp_min_tag = soup.select_one('.temperature .min')
        temp_min = temp_min_tag.text.strip() if temp_min_tag else "—"

        temp_max_tag = soup.select_one('.temperature .max')
        temp_max = temp_max_tag.text.strip() if temp_max_tag else "—"

        desc_tag = soup.select_one('.wDescription .description')
        description = desc_tag.text.strip() if desc_tag else ""

        text = f"🌤 Погода в {city} на {date} {month}:\nМин: {temp_min}\nМакс: {temp_max}\n{description}"
        return text
    except Exception as e:
        return f"Ошибка при получении погоды: {e}"

# === Отправка погоды ===
def send_weather():
    try:
        weather = get_weather()
        bot.send_message(CHAT_ID, weather)
    except Exception as e:
        print("Ошибка при отправке сообщения:", e)

# === Обработчик команды /test ===
@bot.message_handler(commands=['test'])
def handle_test(message):
    weather = get_weather()
    bot.send_message(message.chat.id, f"✅ Проверка: бот работает!\n\n{weather}")

# === Ежедневное расписание ===
def schedule_checker():
    schedule.every().day.at("08:00").do(send_weather)
    while True:
        schedule.run_pending()
        time.sleep(60)

# === Отправляем сообщение при запуске ===
try:
    bot.send_message(CHAT_ID, "✅ Бот запущен и будет отправлять погоду каждый день в 08:00 (по серверному времени).")
except Exception as e:
    print("Не удалось отправить стартовое сообщение:", e)

# === Запуск двух потоков: один слушает Telegram, второй выполняет расписание ===
threading.Thread(target=schedule_checker).start()
bot.polling(none_stop=True)
