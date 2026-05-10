import os
import random
import datetime
import shutil
import sqlite3
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from utils.image_logic import analyze_image
from utils.audio_logic import analyze_audio
from utils.text_logic import analyze_text

app = FastAPI(title="Lok-Setu API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "loksetu.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (username TEXT PRIMARY KEY, password TEXT, role TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS complaints
                 (fir_id TEXT PRIMARY KEY, station_name TEXT, timestamp TEXT, 
                  complainant TEXT, suspect TEXT, category TEXT, 
                  details TEXT, threat_score TEXT, status TEXT)''')
    
    # Pre-seed some default users
    c.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin123', 'admin')")
    c.execute("INSERT OR IGNORE INTO users VALUES ('citizen', 'password123', 'citizen')")
    
    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# --- MODELS ---
class LoginModel(BaseModel):
    username: str
    password: str
    role: str

class RegisterModel(BaseModel):
    username: str
    password: str

class TextScanModel(BaseModel):
    text: str

class UrlScanModel(BaseModel):
    url: str

class UpiScanModel(BaseModel):
    upi: str

class ComplaintModel(BaseModel):
    user_location: str
    victim_name: str
    scammer_id: str
    incident_category: str
    incident_details: str
    threat_score: str

# --- ROUTES ---
@app.get("/")
def serve_frontend():
    return FileResponse("index.html")

@app.post("/api/auth/login")
def login(data: LoginModel):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=? AND role=?", (data.username, data.password, data.role))
    user = c.fetchone()
    conn.close()
    
    if user:
        return {"success": True, "username": user["username"], "role": user["role"]}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/auth/register")
def register(data: RegisterModel):
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (data.username, data.password, 'citizen'))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Username already exists")
    conn.close()
    return {"success": True}

@app.post("/api/scan/text")
def scan_text(data: TextScanModel):
    score = analyze_text(data.text)
    return {"score": score}

@app.post("/api/scan/url")
def scan_url(data: UrlScanModel):
    target_url = data.url
    if "free" in target_url.lower() or "bit.ly" in target_url.lower() or "update" in target_url.lower():
        score = random.uniform(0.85, 0.99) 
    else:
        score = random.uniform(0.01, 0.15)
    return {"score": score}

@app.post("/api/scan/upi")
def scan_upi(data: UpiScanModel):
    target_upi = data.upi
    if "@" in target_upi:
        score = random.uniform(0.75, 0.95) 
    else:
        score = random.uniform(0.10, 0.30)
    return {"score": score}

@app.post("/api/scan/media")
async def scan_media(file: UploadFile = File(...)):
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb+") as file_object:
        shutil.copyfileobj(file.file, file_object)
        
    try:
        if "image" in file.content_type:
            score = analyze_image(file_location)
        elif "audio" in file.content_type:
            score = analyze_audio(file_location)
        else:
            score = 0.0
    except Exception as e:
        print(f"Error analyzing media: {e}")
        score = 0.0
    finally:
        if os.path.exists(file_location):
            os.remove(file_location)
            
    return {"score": score}

@app.post("/api/complaints")
def submit_complaint(data: ComplaintModel):
    station_name = f"{data.user_location.upper()} District Nodal Station"
    fir_id = f"FIR-{random.randint(100000, 999999)}"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO complaints 
                 (fir_id, station_name, timestamp, complainant, suspect, category, details, threat_score, status) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (fir_id, station_name, timestamp, data.victim_name, data.scammer_id, 
               data.incident_category, data.incident_details, data.threat_score, "Pending Investigation"))
    conn.commit()
    conn.close()
    
    return {"success": True, "report": {
        "fir_id": fir_id,
        "station_name": station_name,
        "timestamp": timestamp,
        "complainant": data.victim_name,
        "suspect": data.scammer_id,
        "category": data.incident_category,
        "details": data.incident_details,
        "threat_score": data.threat_score,
        "status": "Pending Investigation"
    }}

@app.get("/api/complaints")
def get_complaints():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM complaints ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return {"complaints": [dict(row) for row in rows]}

@app.get("/api/complaints/user/{username}")
def get_user_complaints(username: str):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM complaints WHERE complainant=? ORDER BY timestamp DESC", (username,))
    rows = c.fetchall()
    conn.close()
    return {"complaints": [dict(row) for row in rows]}

@app.post("/api/complaints/{fir_id}/resolve")
def resolve_complaint(fir_id: str):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE complaints SET status='Resolved' WHERE fir_id=?", (fir_id,))
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Complaint not found")
    conn.commit()
    
    c.execute("SELECT * FROM complaints WHERE fir_id=?", (fir_id,))
    row = c.fetchone()
    conn.close()
    return {"success": True, "report": dict(row)}