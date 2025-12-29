from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt, JWTError
from datetime import datetime, timedelta
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from dotenv import load_dotenv
import bcrypt
import os
import uvicorn

load_dotenv()

app = FastAPI(title="Student Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
security = HTTPBearer(auto_error=True)

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set")

MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    raise RuntimeError("MONGO_URL is not set")

try:
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    client.server_info()
    print("Connected to MongoDB")
except ServerSelectionTimeoutError as e:
    raise RuntimeError(e)

db = client["backend"]
users = db["users"]
students = db["students"]

class UserSignup(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Student(BaseModel):
    student_id: str
    name: str
    age: int
    email: str
    department: str
    gender: str

def create_token(data: dict, expires_minutes: int = 60):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=expires_minutes)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        return jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

@app.get("/")
def root():
    return {"message": "Backend running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

@app.post("/signup")
def signup(data: UserSignup):
    if users.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="Email exists")

    hashed = bcrypt.hashpw(data.password.encode(), bcrypt.gensalt())
    users.insert_one({
        "name": data.name,
        "email": data.email,
        "password": hashed
    })
    return {"message": "User created"}

@app.post("/login")
def login(data: UserLogin):
    user = users.find_one({"email": data.email})
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    if not bcrypt.checkpw(data.password.encode(), user["password"]):
        raise HTTPException(status_code=401, detail="Wrong password")

    token = create_token({"email": user["email"]})
    return {"access_token": token}

@app.post("/students")
def add_student(student: Student, user=Depends(verify_token)):
    if students.find_one({"student_id": student.student_id}):
        raise HTTPException(status_code=400, detail="Student exists")

    students.insert_one(student.model_dump())
    return {"message": "Student added"}

@app.get("/students")
def get_students(user=Depends(verify_token)):
    return list(students.find({}, {"_id": 0}))
