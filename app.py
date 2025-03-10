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

@app.route('/chitiet')
def chitiet():
    return render_template('Chitiet.html')
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
if __name__ == "__main__":
    app.run(debug=True, port=5001)
