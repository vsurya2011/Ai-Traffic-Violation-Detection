from flask import Flask, render_template, request, jsonify
from ultralytics import YOLO
import cv2, os, base64, io, datetime, sqlite3
from PIL import Image
import numpy as np

app = Flask(__name__)

# Load model
model = YOLO("model/yolov8m.pt")

# Create DB if not exists
def init_db():
    conn = sqlite3.connect('violations.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS violations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    violation_type TEXT,
                    timestamp TEXT,
                    img_tag TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('violations.db')
    c = conn.cursor()
    c.execute("SELECT * FROM violations ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return render_template('dashboard.html', data=rows)

@app.route('/detect', methods=['POST'])
def detect():
    file = request.files['frame']
    image = Image.open(file.stream).convert('RGB')
    img = np.array(image)
    results = model.predict(img, conf=0.5)
    
    detected = []
    for box in results[0].boxes.data.tolist():
        cls_id = int(box[5])
        label = model.names[cls_id]
        detected.append(label)
    
    if detected:
        conn = sqlite3.connect('violations.db')
        c = conn.cursor()
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for d in detected:
            c.execute("INSERT INTO violations (violation_type, timestamp, img_tag) VALUES (?, ?, ?)",
                      (d, ts, None))
        conn.commit()
        conn.close()

    return jsonify({"detected": detected})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
