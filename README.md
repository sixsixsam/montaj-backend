Montaj Backend (Firestore-ready)

1) Place your Firebase service account JSON to backend/serviceAccountKey.json (do NOT commit it).
2) Install dependencies:
   python -m venv venv
   venv\Scripts\activate   # Windows
   pip install -r requirements.txt
3) Run:
   uvicorn main:app --reload
4) For deploy (Render), set env var FIREBASE_CREDENTIALS to the full JSON text and CORS_ORIGINS to your frontend origin.
