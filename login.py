from db import get_db_connection  # Import kết nối từ db.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash


login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])  # ✅ Route này thực sự là 'login.login'
def login():
    if request.method == 'POST':
        ten_tai_khoan = request.form.get('username')
        mat_khau = request.form.get('password')

        if not ten_tai_khoan or not mat_khau:
            flash('Vui lòng nhập đầy đủ thông tin!', 'warning')
            return redirect(url_for('login.login'))  # ✅ Gọi chính xác route

        # Kết nối database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT ma_tai_khoan, ten_tai_khoan, mat_khau, ma_quyen
            FROM TaiKhoan
            WHERE ten_tai_khoan = %s
        """, (ten_tai_khoan,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        # So sánh mật khẩu **chưa mã hóa**
        if user and user[2] == mat_khau:  # So sánh trực tiếp với mật khẩu nhập vào
            session['loggedin'] = True
            session['ma_tai_khoan'] = user[0]
            session['ten_tai_khoan'] = user[1]
            session['ma_quyen'] = user[3]

            # ✅ Điều hướng theo quyền người dùng
            if user[3] == '0':  # Admin
                return redirect(url_for('login.admin_home'))
            else:  # Người dùng thường
                return redirect(url_for('login.home'))

        flash('Tên tài khoản hoặc mật khẩu không đúng!', 'danger')

    return render_template('login.html')


@login_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login.login'))  # ✅ Đúng

@login_bp.route('/dangky', methods=['GET', 'POST'])
def dangky():
    if request.method == 'POST':
        ten_tai_khoan = request.form.get('email')
        mat_khau = request.form.get('password')

        if not ten_tai_khoan or not mat_khau:
            flash('Vui lòng nhập đầy đủ thông tin!', 'warning')
            return redirect(url_for('login.dangky'))  # ✅ Đúng

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM TaiKhoan WHERE ten_tai_khoan = %s", (ten_tai_khoan,))
        existing_user = cur.fetchone()

        if existing_user:
            flash('Tài khoản đã tồn tại!', 'danger')
        else:
            hashed_password = generate_password_hash(mat_khau)
            cur.execute("""
                INSERT INTO TaiKhoan (ten_tai_khoan, mat_khau, ma_quyen)
                VALUES (%s, %s, %s)
            """, (ten_tai_khoan, hashed_password, '1'))
            conn.commit()
            flash('Đăng ký thành công! Bạn có thể đăng nhập.', 'success')

        cur.close()
        conn.close()
        return redirect(url_for('login.login'))  # ✅ Đúng

    return render_template('dangky.html')


@login_bp.route('/quenmk')
def quenmk():
    return render_template('quenmk.html')

@login_bp.route('/admin')
def admin_home():
    return render_template('admin/index.html')

@login_bp.route('/user')
def home():
    return render_template('admin/index.html')