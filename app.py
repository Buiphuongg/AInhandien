from flask import Flask, render_template, Response, request, url_for
import cv2
from flask import redirect

from ultralytics import YOLO
import mysql.connector

app = Flask(__name__)
# Kết nối đến MySQL
conn = mysql.connector.connect(
    host="localhost",   # Địa chỉ MySQL Server (thường là localhost)
    user="root",        # Tên đăng nhập MySQL
    password="06102003",# Mật khẩu MySQL
    database="ainhandang"  # Tên database muốn kết nối
)



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
    cur = conn.cursor()
    cur.execute("select * from traicay")
    data = cur.fetchall()
    cur.close()
    return render_template('index.html',traicay = data)

@app.route('/chitietloai')
def detail():
    cur = conn.cursor()
    cur.execute("select * from loaitraicay")
    data1 = cur.fetchall()
    cur.execute("select * from traicay")
    data2 = cur.fetchall()
    cur.close()
    return render_template('chitietloai.html',loaitraicay=data1,traicay=data2)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/insert',methods=['POST'])
def insert():
    if request.method == "POST":
        maloai = request.form['maloai']
        tenloai = request.form['tenloai']
        xuatxu = request.form['xuatxu']
        soluong = request.form['soluong']
        ghichu = request.form['ghichu']
        matraicay = request.form['matraicay']
        cur = conn.cursor()
        cur.execute("insert into loaitraicay (ma_loai,ten_loai,xuat_xu,so_luong,ghi_chu,ma_trai_cay) values (%s,%s,%s,%s,%s,%s)",(maloai,tenloai,xuatxu,soluong,ghichu,matraicay))
        conn.commit()
        cur.close()
        return redirect(url_for('detail'))

@app.route('/delete/<string:maloai>', methods=['GET'])
def delete(maloai):
        cur = conn.cursor()
        cur.execute("DELETE FROM loaitraicay WHERE ma_loai=%s", (maloai,))
        conn.commit()  # Đảm bảo MySQL cập nhật dữ liệu
        cur.close()
        return redirect(url_for('detail'))

@app.route('/update',methods=['POST','GET'])
def update():
    if request.method == 'POST':
        maloai = request.form['maloai']
        tenloai = request.form['tenloai']
        xuatxu = request.form['xuatxu']
        soluong = request.form['soluong']
        ghichu = request.form['ghichu']
        hinhanh= request.form['hinhanh']
        matraicay = request.form['matraicay']
        cur = conn.cursor()
        cur.execute(
            "update loaitraicay set ten_loai=%s, xuat_xu=%s, so_luong=%s, ghi_chu=%s, hinhanh=%s, ma_trai_cay=%s where ma_loai=%s",
            (tenloai, xuatxu, soluong, ghichu, hinhanh,matraicay, maloai))
        conn.commit()
        cur.close()
        return redirect(url_for('detail'))

if __name__ == "__main__":
    app.run(debug=True, port=5001)
