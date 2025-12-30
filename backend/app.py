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

# ------------------ LOAD ENV ------------------
load_dotenv()

# ------------------ APP ------------------
app = FastAPI(title="Student Management API")

# ------------------ CORS ------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # OK for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ SECURITY ------------------
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
security = HTTPBearer(auto_error=True)

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set")

# ------------------ MONGODB ------------------
MONGO_URL = os.getenv("MONGO_URL")

if not MONGO_URL:
    raise RuntimeError("MONGO_URL is not set")

try:
    client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
    client.server_info()
    print("✅ Connected to MongoDB Atlas")
except ServerSelectionTimeoutError as e:
    raise RuntimeError(f"❌ MongoDB connection failed: {e}")

db = client["backend"]
users = db["users"]
students = db["students"]

# ------------------ MODELS ------------------
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


# ------------------ JWT UTILS ------------------
def create_token(data: dict, expires_minutes: int = 60):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(minutes=expires_minutes)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    try:
        return jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or expired token",
        )

# ------------------ ROUTES ------------------
@app.get("/")
def root():
    return {"message": "FastAPI backend is running!"}


@app.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(data: UserSignup):
    if users.find_one({"email": data.email}):
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_password = bcrypt.hashpw(
        data.password.encode(),
        bcrypt.gensalt(),
    )

    users.insert_one({
        "name": data.name,
        "email": data.email,
        "password": hashed_password,
    })

    return {"message": "User created successfully"}


@app.post("/login", status_code=status.HTTP_200_OK)
def login(data: UserLogin):
    user = users.find_one({"email": data.email})

    if not user:
        raise HTTPException(status_code=400, detail="Email not found")

    if not bcrypt.checkpw(data.password.encode(), user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect password")

    token = create_token({"email": user["email"]})
    return {"access_token": token, "token_type": "bearer"}


@app.post("/students", status_code=status.HTTP_201_CREATED)
def add_student(student: Student, user=Depends(verify_token)):
    if students.find_one({"student_id": student.student_id}):
        raise HTTPException(status_code=400, detail="Student ID already exists")

    students.insert_one(student.model_dump())
    return {"message": "Student added successfully"}


@app.get("/students", status_code=status.HTTP_200_OK)
def get_students(user=Depends(verify_token)):
    return list(students.find({}, {"_id": 0}))


@app.get("/students/{student_id}", status_code=status.HTTP_200_OK)
def get_student(student_id: str, user=Depends(verify_token)):
    student = students.find_one(
        {"student_id": student_id},
        {"_id": 0},
    )
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@app.put("/students/{student_id}", status_code=status.HTTP_200_OK)
def update_student(student_id: str, student: Student, user=Depends(verify_token)):
    result = students.update_one(
        {"student_id": student_id},
        {"$set": student.model_dump()},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

    return {
        "message": "Student updated successfully",
        "student": students.find_one(
            {"student_id": student_id},
            {"_id": 0},
        ),
    }


@app.delete("/students/{student_id}", status_code=status.HTTP_200_OK)
def delete_student(student_id: str, user=Depends(verify_token)):
    result = students.delete_one({"student_id": student_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"message": "Student deleted successfully"} 