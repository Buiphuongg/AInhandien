from flask import Flask, render_template, Response
import cv2
from ultralytics import YOLO
import os

app = Flask(__name__)

# 🔹 Danh sách file mô hình YOLO
model_files = ["best_2.pt", "best_3.pt"]
models = []

# 🔹 Load tất cả mô hình
for model_path in model_files:
        model = YOLO(model_path)
        models.append(model)

cap = cv2.VideoCapture(0)

def detect_and_draw(frame):
    """
    Chạy nhận diện trên tất cả mô hình YOLO và vẽ bounding box.
    """
    for model in models:
        results = model(frame)
        class_names = model.names  # Lấy nhãn từ danh sách mô hình đầu tiên

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                confidence = box.conf[0]
                label_id = int(box.cls[0])
                label = class_names[label_id]  # Lấy tên class
                text = f"{label}: {confidence:.2f}"

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    return frame

def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break

        # Chạy nhận diện trên tất cả mô hình
        frame = detect_and_draw(frame)

        # Encode frame thành JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True, port=5001)
