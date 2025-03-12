from flask import Flask, render_template, Response, request
import cv2
import torch
import numpy as np
from ultralytics import YOLO
import os

app = Flask(__name__)

# Load model YOLOv8 đã huấn luyện
model = YOLO("best_2.pt")


# Hàm nhận diện ảnh
def detect_objects(frame):
    results = model(frame)  # Dự đoán với YOLO
    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Tọa độ bbox
            conf = box.conf[0]  # Độ tin cậy
            cls = int(box.cls[0])  # Lớp dự đoán

            # Vẽ khung chữ nhật và hiển thị lớp + độ tin cậy
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{model.names[cls]} {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return frame


# Camera stream
def generate_frames():
    cap = cv2.VideoCapture(0)  # Mở webcam
    while True:
        success, frame = cap.read()
        if not success:
            break
        frame = detect_objects(frame)  # Nhận diện đối tượng
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()


@app.route('/')
def index():
    return render_template('nhanDien.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Upload ảnh để nhận diện
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    # Lưu ảnh tạm thời
    file_path = "static/uploaded.jpg"
    file.save(file_path)

    # Đọc ảnh và nhận diện
    img = cv2.imread(file_path)
    img = detect_objects(img)

    # Lưu ảnh kết quả
    output_path = "static/detected.jpg"
    cv2.imwrite(output_path, img)

    return render_template("nhanDien.html", uploaded=True)


if __name__ == "__main__":
    app.run(debug=True,port=5002)
