from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from typing import Dict, List, Optional
import os
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import face_recognition

app = FastAPI()

# Разрешаем CORS для всех доменов (можно настроить по необходимости)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

NEO4J_USER = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "password")
NEO4J_URL = os.environ.get("NEO4J_URI", "bolt://neo4j:7687")

# Инициализация системы учета посещаемости
attendance_system = AttendanceSystem(NEO4J_URL, NEO4J_USER, NEO4J_PASSWORD)
attendance_system.load_faces_from_db()

@app.get("/upload_image", response_class=HTMLResponse)
async def upload_form():
    return '''
    <!doctype html>
    <title>Face Recognition</title>
    <h1>Upload a picture to recognize faces!</h1>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''

@app.post("/upload_image")
async def upload_image(file: UploadFile = File(...)):
    contents = await file.read()
    img = face_recognition.load_image_file(contents)
    unknown_face_encodings = face_recognition.face_encodings(img)

    faces_found = False
    identified_faces = []

    if unknown_face_encodings:
        faces_found = True
        for unknown_face in unknown_face_encodings:
            identified_faces.extend(attendance_system.compare_faces(unknown_face))

    result = {
        "face_found_in_image": faces_found,
        "who_on_photo": identified_faces
    }
    return result

@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Welcome to CMSE Backend!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)