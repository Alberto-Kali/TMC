import os
import face_recognition
from flask import Flask, jsonify, request, redirect

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Папка с изображениями лиц
directory = 'faces'
faces = []
face_names = []
files = [os.path.join(directory, file) for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))]

# Загрузка изображений и их кодировок
for file in files:
    image = face_recognition.load_image_file(file)
    face_encoding = face_recognition.face_encodings(image)
    if face_encoding:  # Проверяем, есть ли кодировка лица
        faces.append(face_encoding[0])  # Сохраняем только первую кодировку
        face_names.append(os.path.basename(file))  # Сохраняем имя файла без пути

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file and allowed_file(file.filename):
            return detect_faces_in_image(file)

    return '''
    <!doctype html>
    <title>who on pics</title>
    <h1>Upload pics for recognition</h1>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    '''

def detect_faces_in_image(file_stream):
    img = face_recognition.load_image_file(file_stream)
    unknown_face_encodings = face_recognition.face_encodings(img)

    faces_found = False
    identified_faces = []

    if unknown_face_encodings:
        faces_found = True
        for unknown_face in unknown_face_encodings:
            match_results = face_recognition.compare_faces(faces, unknown_face)
            # Проверяем, есть ли совпадения
            for i, match in enumerate(match_results):
                if match:
                    identified_faces.append(face_names[i])  # Добавляем имя соответствующего лица

    result = {
        "face_found_in_image": faces_found,
        "who_on_photo": identified_faces
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)