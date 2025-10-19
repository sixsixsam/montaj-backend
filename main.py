import os
import json
import datetime
from fastapi import FastAPI, Depends, HTTPException, Request, Body
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth, firestore
from dotenv import load_dotenv

# --- Load .env ---
load_dotenv()

# --- Firebase init ---
service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT")
if not service_account_json:
    raise RuntimeError("❌ FIREBASE_SERVICE_ACCOUNT не найден")

cred_dict = json.loads(service_account_json)
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- FastAPI ---
app = FastAPI(title="Montaj Scheduler API")

# --- CORS ---
origins = [
    "http://localhost:5173",
    "https://sistemab-montaj-6b8c1.web.app",
    "https://sistemab-montaj-6b8c1.firebaseapp.com"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# --- Auth dependency ---
def verify_firebase_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(401, "Missing Authorization header")
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(401, "Invalid auth header")
    id_token = parts[1]
    try:
        decoded = firebase_auth.verify_id_token(id_token)
    except Exception as e:
        raise HTTPException(401, "Invalid token: " + str(e))
    uid = decoded.get("uid")
    email = decoded.get("email")
    return {"uid": uid, "email": email, "role": "admin"}  # все пока админы

# --- Auth route ---
@app.post("/api/auth/login")
def login_route(user=Depends(verify_firebase_token)):
    return {"uid": user["uid"], "email": user["email"], "role": user["role"]}

# --- Health check ---
@app.get("/api/health")
def health():
    return {"ok": True}

# --- Workers ---
@app.get("/api/workers", dependencies=[Depends(verify_firebase_token)])
def list_workers():
    docs = db.collection("workers").stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

@app.post("/api/workers", dependencies=[Depends(verify_firebase_token)])
def create_worker(payload: dict = Body(...)):
    doc = db.collection("workers").document()
    doc.set(payload)
    return {"id": doc.id, **payload}

# --- Assignments ---
@app.get("/api/assignments", dependencies=[Depends(verify_firebase_token)])
def list_assignments():
    docs = db.collection("assignments").stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

@app.post("/api/assignments", dependencies=[Depends(verify_firebase_token)])
def create_assignment(payload: dict = Body(...)):
    doc = db.collection("assignments").document()
    doc.set(payload)
    return {"id": doc.id, **payload}

@app.delete("/api/assignments/{assignment_id}", dependencies=[Depends(verify_firebase_token)])
def delete_assignment(assignment_id: str):
    db.collection("assignments").document(assignment_id).delete()
    return {"ok": True}

# --- Projects ---
@app.get("/api/projects", dependencies=[Depends(verify_firebase_token)])
def list_projects():
    docs = db.collection("projects").stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

@app.post("/api/projects", dependencies=[Depends(verify_firebase_token)])
def create_project(payload: dict = Body(...), user=Depends(verify_firebase_token)):
    payload["manager_uid"] = user["uid"]
    doc = db.collection("projects").document()
    doc.set(payload)
    return {"id": doc.id, **payload}

# --- Comments ---
@app.get("/api/comments/{worker_id}", dependencies=[Depends(verify_firebase_token)])
def get_comments(worker_id: str):
    docs = db.collection("comments").where("worker_id", "==", worker_id).stream()
    return [d.to_dict() for d in docs]

@app.post("/api/comments", dependencies=[Depends(verify_firebase_token)])
def add_comment(payload: dict = Body(...), user=Depends(verify_firebase_token)):
    payload["author_uid"] = user["uid"]
    payload["created_at"] = datetime.datetime.utcnow().isoformat()
    doc = db.collection("comments").document()
    doc.set(payload)
    return {"id": doc.id, **payload}
