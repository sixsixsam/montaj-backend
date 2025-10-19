import os
import json
import datetime
from fastapi import FastAPI, Depends, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth, firestore
from dotenv import load_dotenv

# --- Загружаем .env ---
load_dotenv()

# --- Firebase init ---
service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
if not service_account_json:
    raise RuntimeError("❌ FIREBASE_SERVICE_ACCOUNT не найден в переменных окружения.")

try:
    cred_dict = json.loads(service_account_json)
except Exception as e:
    raise RuntimeError(f"Ошибка при парсинге FIREBASE_SERVICE_ACCOUNT: {e}")

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

firestore_db = firestore.client()

# --- FastAPI ---
app = FastAPI(title="Montaj Scheduler API (Firestore)")

# --- CORS ---
origins = [
    "https://sistemab-montaj-6b8c1.web.app",
    "https://sistemab-montaj-6b8c1.firebaseapp.com",
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- Auth dependency без ролей ---
def verify_firebase_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    parts = auth_header.split()
    if parts[0].lower() != "bearer" or len(parts) != 2:
        raise HTTPException(status_code=401, detail="Invalid auth header")
    id_token = parts[1]
    try:
        decoded = firebase_auth.verify_id_token(id_token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token: " + str(e))
    uid = decoded.get("uid")
    email = decoded.get("email")
    return {"uid": uid, "email": email}

# --- Login route для фронтенда ---
@app.post("/api/auth/login")
def login_route(user=Depends(verify_firebase_token)):
    # Временно все админы, чтобы показать функционал
    return {"uid": user["uid"], "email": user["email"], "role": "admin"}

# --- Остальные endpoint'ы ---
@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/workers", dependencies=[Depends(verify_firebase_token)])
def list_workers():
    docs = firestore_db.collection("workers").order_by("name").stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

@app.post("/api/workers", dependencies=[Depends(verify_firebase_token)])
def create_worker(payload: dict = Body(...)):
    doc = firestore_db.collection("workers").document()
    doc.set(payload)
    return {"id": doc.id, **payload}

@app.get("/api/workers/{worker_id}/schedule", dependencies=[Depends(verify_firebase_token)])
def worker_schedule(worker_id: str, days: int = 60):
    today = datetime.date.today()
    end = today + datetime.timedelta(days=days)
    assignments_q = firestore_db.collection("assignments").where("worker_id", "==", worker_id).stream()
    assignments = [a.to_dict() for a in assignments_q]
    current = None
    next_assign = None
    for a in assignments:
        s = datetime.date.fromisoformat(a["start_date"])
        e = datetime.date.fromisoformat(a["end_date"])
        if s <= today <= e:
            current = a
        if s > today and (not next_assign or s < datetime.date.fromisoformat(next_assign["start_date"])):
            next_assign = a

    calendar = []
    cur = today
    while cur <= end:
        cell = None
        for a in assignments:
            s = datetime.date.fromisoformat(a["start_date"])
            e = datetime.date.fromisoformat(a["end_date"])
            if s <= cur <= e:
                proj = firestore_db.collection("projects").document(a["project_id"]).get()
                pname = proj.to_dict().get("name") if proj.exists else None
                cell = {"date": cur.isoformat(), "project": pname, "project_id": a["project_id"]}
                break
        calendar.append(cell)
        cur += datetime.timedelta(days=1)

    history_q = firestore_db.collection("assignment_history").where("worker_id", "==", worker_id).order_by("start_date").stream()
    history = [h.to_dict() for h in history_q]

    worker_doc = firestore_db.collection("workers").document(worker_id).get()
    worker = worker_doc.to_dict() if worker_doc.exists else {"id": worker_id, "name": "Unknown", "phone": None, "active": True}

    return {"worker": worker, "current": current, "next": next_assign, "calendar": calendar, "history": history}

@app.post("/api/assignments", dependencies=[Depends(verify_firebase_token)])
def create_assignment(payload: dict = Body(...)):
    doc = firestore_db.collection("assignments").document()
    doc.set(payload)
    return {"id": doc.id, **payload}

@app.delete("/api/assignments/{assignment_id}", dependencies=[Depends(verify_firebase_token)])
def delete_assignment(assignment_id: str):
    a_doc = firestore_db.collection("assignments").document(assignment_id).get()
    if not a_doc.exists:
        raise HTTPException(status_code=404, detail="Not found")
    firestore_db.collection("assignments").document(assignment_id).delete()
    return {"ok": True}

@app.get("/api/projects", dependencies=[Depends(verify_firebase_token)])
def list_projects():
    docs = firestore_db.collection("projects").order_by("name").stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

@app.post("/api/projects", dependencies=[Depends(verify_firebase_token)])
def create_project(payload: dict = Body(...), user=Depends(verify_firebase_token)):
    doc = firestore_db.collection("projects").document()
    payload["manager_uid"] = user["uid"]
    doc.set(payload)
    return {"id": doc.id, **payload}
