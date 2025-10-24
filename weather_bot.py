import requests
from bs4 import BeautifulSoup
import telebot
import schedule
import time

# === Настройки ===
TOKEN = "8261592064:AAFLThqLcAnSBdlSWWon1596-X_zByVo9rY"
CHAT_ID = -1002548699204
CITY_URL = "https://sinoptik.ua/пogoda-dnepr"  # альтернативная форма URL, если потребуется

bot = telebot.TeleBot(TOKEN)

def get_weather():
    try:
        # Попытка получить и спарсить страницу sinoptik
        response = requests.get("https://sinoptik.ua/погода-днепр", timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Попытки разных селекторов — сайт может меняться, поэтому используем безопасные проверки
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
        return text.format(city=city, date=date, month=month, temp_min=temp_min, temp_max=temp_max, description=description)
    except Exception as e:
        return f"Ошибка при получении погоды: {e}"

def send_weather():
    try:
        weather = get_weather()
        bot.send_message(CHAT_ID, weather)
    except Exception as e:
        # Логируем ошибку в консоль — на Render можно посмотреть логи
        print("Ошибка при отправке сообщения:", e)

# Отправляем стартовое уведомление один раз при запуске
try:
    bot.send_message(CHAT_ID, "✅ Бот запущен и будет отправлять погоду каждый день в 08:00 (по серверному времени).")
except Exception as e:
    print("Не удалось отправить стартовое сообщение:", e)

# Планируем ежедневную задачу в 08:00
schedule.every().day.at("08:00").do(send_weather)
@bot.message_handler(commands=['test'])
def handle_test(message):
    send_weather()
print("Запущен цикл расписания. Ожидание...")
while True:
    schedule.run_pending()
    time.sleep(60)
