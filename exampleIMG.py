import os
import json
import requests
from PIL import Image
import io
import base64

url = "https://docs.python-requests.org/en/latest/_static/requests-sidebar.png"
filepath = "image.jpg"
jsonpath = "todo_source.json"

data = {
    "name": "name",
    "old": "old",
    "work": "work",
    "education": "education"
}

def down_imgPrev():
    response = requests.get(url)
    if response.status_code == 200:
        image = Image.open(io.BytesIO(response.content))
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        image.save(filepath)
        print(f"Image saved: '{filepath}'")

        # Кодируем изображение в base64
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # Добавляем превью в JSON
        data["preview"] = img_str

        with open(jsonpath, "w", encoding="utf-8") as todo_source:
            json.dump(data, todo_source, ensure_ascii=False, indent=4)
        print(f"JSON сохранён: '{jsonpath}'")

down_imgPrev()
