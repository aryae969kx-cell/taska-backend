from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="TASKA Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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
    title = order.get("title", "")
    description = order.get("description", "")
    category = order.get("category", "")
    budget = order.get("budget", "")
    deadline = order.get("deadline", "")

    return {
        "success": True,
        "tz": {
            "task": title,
            "category": category,
            "requirements": description,
            "budget": f"{budget} ₽",
            "deadline": deadline
        }
    }
