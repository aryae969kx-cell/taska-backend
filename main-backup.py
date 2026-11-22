
import os
import json
import urllib.request
import urllib.error

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="TASKA Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "TASKA backend is running 🚀"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/api/create-tz")
def create_tz(order: dict):
    api_key = os.getenv("YANDEX_API_KEY")
    folder_id = os.getenv("YANDEX_FOLDER_ID")

    if not api_key or not folder_id:
        raise HTTPException(
            status_code=500,
            detail="Yandex API key or folder ID is missing"
        )

    title = str(order.get("title", "")).strip()
    description = str(order.get("description", "")).strip()
    category = str(order.get("category", "")).strip()
    budget = str(order.get("budget", "")).strip()
    deadline = str(order.get("deadline", "")).strip()

    if not title and not description:
        raise HTTPException(
            status_code=400,
            detail="Please provide an order title or description"
        )

    prompt = f"""
Составь профессиональное и понятное техническое задание
для исполнителя на бирже TASKA.

Данные клиента:
Название: {title}
Категория: {category}
Описание: {description}
Бюджет: {budget or "Не указан"}
Срок: {deadline or "Не указан"}

Требования:
1. Кратко и понятно опиши суть задачи.
2. Распиши требования к результату.
3. Укажи, что именно исполнитель должен передать заказчику.
4. Если информации недостаточно, перечисли вопросы,
   которые нужно уточнить у заказчика.
5. Не придумывай отсутствующие детали, бюджет и сроки.
6. Пиши на русском языке.
7. Сделай текст удобным для чтения с телефона.
"""

    request_data = {
        "model": f"gpt://{folder_id}/yandexgpt-5.1",
        "messages": [
            {
                "role": "system",
                "content": (
                    "Ты профессиональный менеджер проектов TASKA. "
                    "Помогаешь клиентам создавать точные технические задания."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.3
    }

    req = urllib.request.Request(
        "https://ai.api.cloud.yandex.net/v1/chat/completions",
        data=json.dumps(request_data).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {api_key}",
            "OpenAI-Project": folder_id
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))

        ai_text = result["choices"][0]["message"]["content"]

        if not ai_text:
            raise ValueError("Empty AI response")

    except urllib.error.HTTPError as error:
        error_body = error.read().decode("utf-8", errors="replace")
        print("Yandex API error:", error.code, error_body)

        raise HTTPException(
            status_code=502,
            detail=f"Yandex AI returned error {error.code}"
        )

    except Exception as error:
        print("AI request error:", str(error))

        raise HTTPException(
            status_code=502,
            detail="Could not generate technical specification"
        )

    return {
        "success": True,
        "tz": {
            "task": title,
            "category": category,
            "requirements": ai_text,
            "budget": f"{budget} ₽" if budget else "Не указан",
            "deadline": deadline or "Не указан"
        }
    }
