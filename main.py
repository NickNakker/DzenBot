import os
import time
import re
import threading
import schedule
import html
from dotenv import load_dotenv
from openai import OpenAI
import telebot
from yandex_cloud_ml_sdk import YCloudML
import textwrap


load_dotenv()

bot = telebot.TeleBot(os.getenv('TG_TOKEN'))
CHAT_ID = os.getenv('TG_CHAT_ID')
deepseek_api = os.getenv('DEEPSEEK_API_KEY')

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=deepseek_api,
)

IMAGE_FOLDER = "generated_images"
os.makedirs(IMAGE_FOLDER, exist_ok=True)

def generate_response(prompt: str) -> str:
    response = client.chat.completions.create(
        model="deepseek/deepseek-r1-0528:free",
        messages=[
            {"role": "system", "content": "Ты профессиональный копирайтер"},
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    return response.choices[0].message.content

def generate_image(description: str):
    try:
        sdk = YCloudML(
            folder_id=os.getenv('YANDEX_FOLDER_ID'),
            auth=os.getenv('YANDEX_API_KEY')
        )
        model = sdk.models.image_generation("yandex-art").configure(width_ratio=1, height_ratio=1)
        image_path = os.path.join(IMAGE_FOLDER, f"img_{int(time.time())}.jpg")
        operation = model.run_deferred([description])
        result = operation.wait()

        with open(image_path, "wb") as f:
            f.write(result.image_bytes)

        return image_path
    except Exception as e:
        print(f"❌ Ошибка генерации изображения: {e}")
        return None

def extract_photo_description(text: str):
    match = re.search(r'\[ФОТО:(.*?)\]', text, re.DOTALL)
    if not match:
        return None, text
    desc = match.group(1).strip()
    cleaned_text = text.replace(match.group(0), "").strip()
    return desc, cleaned_text

def truncate_text(text: str, limit: int = 1024) -> str:
    return text if len(text) <= limit else text[:limit - 3] + "..."

def sanitize_html(text: str) -> str:
    """Преобразует нестандартные HTML-теги в допустимые для Telegram"""
    text = re.sub(r'</?(h1|h2|h3|h4|h5|h6)>', '<b>', text)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</?(div|span|p)>', '', text)
    return text

def scheduled_task():
    prompt = """
Сгенерируй популярный пост для Яндекс.Дзен длиной 800 символов с HTML-разметкой (b, i, a, h1). 
Добавь описание изображения в формате [ФОТО: ...]. Пример:

<h1>Как мышь спасла город</h1>
<i>История, которую вы не слышали</i>
[ФОТО: старая карта, на которой изображена мышь, сидящая на бочке с порохом в подвале замка]
    """
    try:
        result = generate_response(prompt)
        photo_desc, clean_text = extract_photo_description(result)

        if not photo_desc:
            print("❌ Не найдено описание фото. Отправляем только текст.")
            bot.send_message(CHAT_ID, truncate_text(sanitize_html(clean_text)), parse_mode="HTML")
            return

        image_path = generate_image(photo_desc)
        if not image_path:
            print("❌ Не удалось сгенерировать изображение.")
            bot.send_message(CHAT_ID, truncate_text(sanitize_html(clean_text)), parse_mode="HTML")
            return

        lines = clean_text.strip().split("\n")
        caption_raw = "\n".join(lines[:2]) if len(lines) > 1 else lines[0]
        caption = truncate_text(sanitize_html(caption_raw.strip()), 1024)

        with open(image_path, "rb") as img:
            bot.send_photo(
                CHAT_ID,
                photo=img,
                caption=caption,
                parse_mode="HTML"
            )

        print("✅ Пост опубликован с фото")

        if os.path.exists(image_path):
            os.remove(image_path)

    except Exception as e:
        print(f"Ошибка при отправке: {e}")

def run_scheduler():
    schedule.every(15).minutes.do(scheduled_task)
    while True:
        schedule.run_pending()
        time.sleep(1)

# Первый запуск сразу
scheduled_task()

# Фоновый планировщик
threading.Thread(target=run_scheduler, daemon=True).start()

# Основной цикл бота
bot.polling(none_stop=True)
