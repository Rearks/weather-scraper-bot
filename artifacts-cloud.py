import pandas as pd
import matplotlib.pyplot as plt
import re
from google.cloud import storage
from io import StringIO, BytesIO
import base64


def analyze_weather(request):
    """Cloud Function для генерации графиков"""

    # Читаем данные из Cloud Storage
    client = storage.Client()
    bucket = client.bucket('weather-data-bucket-12345')
    blob = bucket.blob('weather_data.csv')

    try:
        csv_data = blob.download_as_text()
    except:
        return "Нет данных для анализа"

    df = pd.read_csv(StringIO(csv_data))

    # Обработка температуры
    def process_temperature(temp_str):
        numbers = re.findall(r'[+-]?\d+', str(temp_str))
        if numbers:
            return int(numbers[0])
        return 0

    df["temp_numeric"] = df["temp"].apply(process_temperature)

    # Создание графика
    plt.figure(figsize=(10, 6))
    plt.plot(df["date"], df["temp_numeric"], marker="o")
    plt.title("Динамика температуры")
    plt.xlabel("Дата")
    plt.ylabel("Температура °C")
    plt.xticks(rotation=45)
    plt.axhline(y=0, color='r', linestyle='--', alpha=0.7)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    # Сохранение в память
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)

    # Возвращаем изображение
    img_base64 = base64.b64encode(img_buffer.read()).decode()

    return {"image": img_base64}