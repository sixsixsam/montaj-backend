import os
import json
import base64
from fastapi import FastAPI
from .api import router as api_router

import firebase_admin
from firebase_admin import credentials, firestore

# --- Инициализация Firebase через переменную окружения ---
firebase_key_b64 = os.environ.get("FIREBASE_KEY_B64")

if not firebase_key_b64:
    raise RuntimeError("❌ FIREBASE_KEY_B64 не задана в переменных окружения")

try:
    key_json = base64.b64decode(firebase_key_b64).decode("utf-8")
    cred_dict = json.loads(key_json)
    cred = credentials.Certificate(cred_dict)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    print("✅ Firebase initialized from environment variable")
except Exception as e:
    raise RuntimeError(f"❌ Ошибка инициализации Firebase: {e}")

# Клиент Firestore
firestore_db = firestore.client()

# --- FastAPI ---
app = FastAPI(title="Montaj Scheduler API")

# --- Seed admin ---
def seed_admin():
    users_ref = firestore_db.collection("users")
    admin_doc = users_ref.document("admin").get()
    if not admin_doc.exists:
        users_ref.document("admin").set({
            "username": "admin",
            "full_name": "Администратор",
            "role": "admin",
            "hashed_password": "$2b$12$9ZuYc8hE6Kz..."  # TODO: настоящий bcrypt
        })
        print("✅ Seeded admin/adminpass")
    else:
        print("ℹ️ Admin уже существует")

@app.on_event("startup")
def startup_event():
    seed_admin()

# --- Подключаем маршруты ---
app.include_router(api_router, prefix="/api")
