from flask import Flask, render_template, Response, request, url_for
import cv2
from flask import redirect
from ultralytics import YOLO
import mysql.connector
from khayHang import khayhang
from traiCay import traiCay
from chiTietLoai import chiTietLoai
from nhanDien import nhanDien
from duLieuHinhAnh import duLieuHinhAnh
from thongKe import thongKe
from login import login_bp
from db import get_db_connection  # Import kết nối từ db.py

app = Flask(__name__)
app.register_blueprint(khayhang)
app.register_blueprint(traiCay)
app.register_blueprint(chiTietLoai)
app.register_blueprint(nhanDien)
app.register_blueprint(duLieuHinhAnh)
app.register_blueprint(thongKe)
app.register_blueprint(login_bp)

@app.route('/')
def index():
    conn = get_db_connection()  # Tạo kết nối mới
    cur = conn.cursor()
    cur.execute("select * from traicay")
    data = cur.fetchall()
    cur.close()
    return render_template('index.html',traicay = data)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
