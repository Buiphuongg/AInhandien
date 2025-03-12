from flask import Flask, render_template, Response, request, url_for
import cv2
from flask import redirect

from ultralytics import YOLO
import mysql.connector

app = Flask(__name__)
model = YOLO("best.pt")  # Sử dụng YOLOv8

# Kết nối đến MySQL
conn = mysql.connector.connect(
    host="localhost",   # Địa chỉ MySQL Server (thường là localhost)
    user="root",        # Tên đăng nhập MySQL
    password="06102003",# Mật khẩu MySQL
    database="ainhandang"  # Tên database muốn kết nối
)

@app.route('/')
def index():
    cur = conn.cursor()
    cur.execute("select * from traicay")
    data = cur.fetchall()
    cur.close()
    return render_template('index.html',traicay = data)

@app.route('/traicay')
def traicay():
    timkiem = request.args.get('timkiem', '')

    cur = conn.cursor()
    if timkiem:
        cur.execute(
            "SELECT * FROM traicay WHERE ten_trai_cay LIKE %s OR ma_trai_cay LIKE %s OR  ghi_chu LIKE %s",
            ( "%" + timkiem + "%", "%" + timkiem + "%", "%" + timkiem + "%")
        )
    else:
        cur.execute("SELECT * FROM traicay")

    data = cur.fetchall()
    cur.close()
    return render_template('traiCay.html',traicay = data)

@app.route('/chitiet', methods=['GET', 'POST'])
def chitiet():
    timkiem = request.args.get('timkiem', '')

    cur = conn.cursor()

    if timkiem:
        cur.execute(
            "SELECT * FROM loaitraicay WHERE ten_loai LIKE %s OR xuat_xu LIKE %s OR so_luong LIKE %s OR ma_trai_cay LIKE %s OR ghi_chu LIKE %s",
            ("%" + timkiem + "%", "%" + timkiem + "%", "%" + timkiem + "%", "%" + timkiem + "%", "%" + timkiem + "%")
        )
    else:
        cur.execute("SELECT * FROM loaitraicay")

    data1 = cur.fetchall()

    cur.execute("SELECT * FROM traicay")
    data2 = cur.fetchall()

    cur.close()
    return render_template('chiTietLoai.html', loaitraicay=data1, traicay=data2, timkiem=timkiem)

@app.route('/nhandien')
def nhandien():
    return render_template('nhanDien.html')


@app.route('/insert',methods=['POST'])
def insert():
    if request.method == "POST":
        maloai = request.form['maloai']
        tenloai = request.form['tenloai']
        xuatxu = request.form['xuatxu']
        soluong = request.form['soluong']
        ghichu = request.form['ghichu']
        matraicay = request.form['matraicay']
        hinhanh = request.form['hinhanh']
        cur = conn.cursor()
        cur.execute("insert into loaitraicay (ma_loai,ten_loai,xuat_xu,so_luong,ghi_chu,ma_trai_cay,hinhanh) values (%s,%s,%s,%s,%s,%s,%s)",(maloai,tenloai,xuatxu,soluong,ghichu,matraicay,hinhanh))
        conn.commit()
        cur.close()
        return redirect(url_for('chitiet'))

@app.route('/delete/<string:maloai>', methods=['GET'])
def delete(maloai):
        cur = conn.cursor()
        cur.execute("DELETE FROM loaitraicay WHERE ma_loai=%s", (maloai,))
        conn.commit()  # Đảm bảo MySQL cập nhật dữ liệu
        cur.close()
        return redirect(url_for('chitiet'))

@app.route('/delete1/<string:matraicay>', methods=['GET'])
def delete1(matraicay):
        cur = conn.cursor()
        cur.execute("DELETE FROM traicay WHERE ma_trai_cay=%s", (matraicay,))
        conn.commit()  # Đảm bảo MySQL cập nhật dữ liệu
        cur.close()
        return redirect(url_for('traicay'))

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
        return redirect(url_for('chitiet'))

@app.route('/insert1',methods=['POST'])
def insert1():
    if request.method == "POST":
        matraicay = request.form['matraicay']
        tentraicay = request.form['tentraicay']
        ghichu = request.form['ghichu']
        hinhanh = request.form['hinhanh']
        cur = conn.cursor()
        cur.execute("insert into traicay (ma_trai_cay,ten_trai_cay,ghi_chu,hinh_anh) values (%s,%s,%s,%s)",(matraicay,tentraicay,ghichu,hinhanh))
        conn.commit()
        cur.close()
        return redirect(url_for('traicay'))

@app.route('/update1',methods=['POST','GET'])
def update1():
    if request.method == 'POST':
        matraicay = request.form['matraicay']
        tentraicay = request.form['tentraicay']
        ghichu = request.form['ghichu']
        hinhanh = request.form['hinhanh']
        cur = conn.cursor()
        cur.execute(
            "update traicay set ma_trai_cay=%s, ten_trai_cay=%s, ghi_chu=%s, hinh_anh=%s where ma_trai_cay=%s",
            (matraicay,tentraicay,ghichu,hinhanh,matraicay))
        conn.commit()
        cur.close()
        return redirect(url_for('traicay'))

# Hàm nhận diện ảnh
def detect_objects(frame):
    results = model(frame)  # Dự đoán với YOLO
    for result in results:
        for box in result.boxes:
            conf = float(box.conf[0])  # Độ tin cậy
            if conf > 0.6:  # Chỉ hiển thị nếu độ tin cậy lớn hơn 0.6
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Tọa độ bbox
                cls = int(box.cls[0])  # Lớp dự đoán

                # Kiểm tra model.names có tồn tại không
                if hasattr(model, "names") and cls in model.names:
                    label = f"{model.names[cls]} {conf:.2f}"
                else:
                    label = f"Object {cls} {conf:.2f}"

                # Vẽ khung chữ nhật
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Hiển thị nhãn
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

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

import os
from werkzeug.utils import secure_filename

# Thư mục lưu ảnh
UPLOAD_FOLDER = "static/img/upload/"
DETECT_FOLDER = "static/img/detect/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DETECT_FOLDER, exist_ok=True)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file uploaded", 400

    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    # Lấy tên file gốc và đảm bảo an toàn
    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Đọc ảnh và nhận diện
    img = cv2.imread(file_path)

    # Dùng detect_objects để nhận diện ảnh và lấy số lượng quả hỏng
    count_dict = {"rotten_apple": 0, "rotten_banana": 0, "rotten_mango": 0, "rotten_orange": 0, "rotten_peach": 0,
                  "rotten_pear": 0}
    results = model(img)  # Dự đoán với YOLO

    for result in results:
        for box in result.boxes:
            conf = float(box.conf[0])  # Độ tin cậy
            cls = int(box.cls[0])  # Lớp dự đoán

            if conf > 0.5:
                nhan_dang = model.names[cls]  # Lấy tên lớp từ model
                if nhan_dang in count_dict:
                    count_dict[nhan_dang] += 1  # Cập nhật số lượng quả hỏng

                # Vẽ khung trên ảnh
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Lấy tọa độ bbox
                label = f"{nhan_dang} {conf:.2f}"

                # Vẽ hình chữ nhật
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Hiển thị nhãn
                cv2.putText(img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    total_rotten = sum(count_dict.values())  # Tính tổng số quả hỏng

    # Lưu vào database
    cur = conn.cursor()
    cur.execute("INSERT INTO dulieuhinhanh (duong_dan_hinh_anh, ngay_chup, so_luong_hu_hong) VALUES (%s, NOW(), %s)",
                (file_path, total_rotten))
    conn.commit()
    cur.close()

    # Lưu ảnh kết quả với cùng tên
    output_path = os.path.join(DETECT_FOLDER, filename)
    cv2.imwrite(output_path, img)  # Lưu lại ảnh có nhãn

    return render_template("nhanDien.html", uploaded=True, detected_image=output_path)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
