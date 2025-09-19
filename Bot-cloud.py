import requests
import json
import os


def get_handle_url(handle_name):
    tg_token = os.environ.get('TG_TOKEN')
    return f"https://api.telegram.org/bot{tg_token}/{handle_name}"

def send_message(chat_id, text):
    tg_token = os.environ.get('TG_TOKEN')
    response = requests.post(
        f"https://api.telegram.org/bot{tg_token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": text
        }
    )
    return response


def send_photo(chat_id, photo_data, caption=None):
    tg_token = os.environ.get('TG_TOKEN')
    files = {'photo': photo_data}
    data = {'chat_id': chat_id}
    if caption:
        data['caption'] = caption

    response = requests.post(
        f"https://api.telegram.org/bot{tg_token}/sendPhoto",
        files=files,
        data=data
    )
    return response


def get_weather():
    weather_url = "https://us-central1-charged-atlas-472011-r3.cloudfunctions.net/weatherscraper"
    try:
        response = requests.get(weather_url)
        if response.status_code == 200:
            return response.text
        else:
            return "Ошибка получения данных о погоде"
    except Exception as e:
        return f"Ошибка: {str(e)}"


def get_weather_chart():
    chart_url = "https://us-central1-charged-atlas-472011-r3.cloudfunctions.net/weather-analytics"
    try:
        response = requests.get(chart_url)
        if response.status_code == 200:
            data = response.json()
            image_base64 = data.get('image')
            if image_base64:
                import base64
                import io
                image_data = base64.b64decode(image_base64)
                return io.BytesIO(image_data)
        return None
    except Exception as e:
        return None


def telegram_webhook(request):
    """Точка входа для webhook"""

    # Получаем данные
    update = request.get_json()

    if not update:
        return "OK"

    # Извлекаем сообщение
    message = update.get('message')
    if not message:
        return "OK"

    text = message.get('text', '')
    chat_id = message.get('chat', {}).get('id')

    if not chat_id:
        return "OK"

    # Обработка команд
    if text == '/weather':
        weather_data = get_weather()
        send_message(chat_id, weather_data)

    elif text == '/chart':
        chart_data = get_weather_chart()
        if chart_data:
            send_photo(chat_id, chart_data, "График температуры")
        else:
            send_message(chat_id, "Не удалось создать график")

    elif text == '/start':
        help_text = """
Доступные команды:
/weather - текущая погода
/chart - график температуры
"""
        send_message(chat_id, help_text)

    return "OK"