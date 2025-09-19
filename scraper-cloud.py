import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
import os
from google.cloud import storage
import io

def get_weather_data():
    url = "https://www.yr.no/en/forecast/daily-table/2-524901/Russia/Moscow/Moscow"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        temp_element = soup.find('div', class_='now-hero__next-hour-temperature-text')

        if temp_element:
            temp_text = temp_element.text.strip()
            day = datetime.now().strftime("%Y-%m-%d")
            return day, temp_text
    return None

def save_to_cloud_storage(day, temp):
    client = storage.Client()
    bucket = client.bucket('weather-data-bucket-12345')
    blob = bucket.blob('weather_data.csv')

    try:
        existing_data = blob.download_as_text()
    except:
        existing_data = "timestamp,date,temp\n"

    new_row = f"{datetime.now().isoformat()},{day},{temp}\n"
    updated_data = existing_data + new_row
    # Сохраняем
    blob.upload_from_string(updated_data)

def weather_scraper(request):
    """Точка входа"""
    result = get_weather_data()
    if result:
        day, temp = result
        save_to_cloud_storage(day, temp)
        print(f"Собрана температура: {day} - {temp}")
        return f"Погода сегодня: {day} - {temp}"
    else:
        return "Не удалось загрузить"