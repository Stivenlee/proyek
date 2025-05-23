from flask import Flask, render_template, session, request, redirect, url_for, flash
import mysql.connector
from datetime import datetime

app = Flask(__name__)

app.secret_key = "secret"

# Konfigurasi MySQL
app.config['MYSQL_HOST'] = 'cardatabase.c7wec4ugoiuo.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'proyekaws2606'
app.config['MYSQL_DB'] = 'car_rental_dbs'

# Fungsi untuk membuka koneksi ke database
def get_db_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

@app.route("/")
def home():
    return render_template("main.html")

@app.route("/sewa")
def sewa():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM cars")
    cars = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("sewa.html", cars=cars)

@app.route("/update-stock", methods=["POST"])
def update_stock():
    if session.get("role") != "admin":
        flash("Akses ditolak. Hanya admin yang dapat mengubah stok.")
        return redirect(url_for("sewa"))

    car_id = request.form.get("car_id")
    action = request.form.get("action")

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT stock FROM cars WHERE car_id = %s", (car_id,))
    result = cur.fetchone()

    if result:
        current_stock = result["stock"]
        if action == "increase":
            new_stock = current_stock + 1
        elif action == "decrease":
            new_stock = max(0, current_stock - 1)
        else:
            flash("Aksi tidak dikenali.")
            cur.close()
            conn.close()
            return redirect(url_for("sewa"))

        cur.execute("UPDATE cars SET stock = %s WHERE car_id = %s", (new_stock, car_id))
        conn.commit()
        flash(f"Stok berhasil diubah: sekarang {new_stock}")
    else:
        flash("Mobil tidak ditemukan.")

    cur.close()
    conn.close()
    return redirect(url_for("sewa"))

@app.route("/sign-in", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT user_id, username, email, password, role FROM users WHERE username = %s AND email = %s", (username, email))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            conn = get_db_connection()
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            username_check = cur.fetchone()
            cur.close()
            conn.close()
            if username_check:
                return render_template("sign_in.html", error_field="email", error_message="Email tidak cocok")
            else:
                return render_template("sign_in.html", error_field="username", error_message="Username tidak ditemukan")

        if user["password"] != password:
            return render_template("sign_in.html", error_field="password", error_message="Password salah")

        session["user_id"] = user["user_id"]
        session["username"] = user["username"]
        session["role"] = user["role"]
        session["email"] = user["email"]

        return redirect(url_for("home"))

    return render_template("sign_in.html")

@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        username = request.form.get("username")
        phone = request.form.get("phone_number")
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            cur.close()
            conn.close()
            flash("Email sudah terdaftar!")
            return redirect(url_for("sign_up"))

        cur.execute("""
            INSERT INTO users (username, password, email, phone_number, role) 
            VALUES (%s, %s, %s, %s, 'member')
        """, (username, password, email, phone))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for("sign_in"))

    return render_template("sign_up.html")

@app.route("/rent_car", methods=["POST"])
def rent_car():
    if not session.get('user_id'):
        return redirect(url_for('sign_in'))

    user_id = session.get('user_id')
    car_id = request.form.get('car_id')  
    rental_date = request.form.get('rental_date')
    return_date = request.form.get('return_date')

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT price_per_day, stock FROM cars WHERE car_id = %s", (car_id,))
    car = cur.fetchone()

    if not car or car["stock"] <= 0:
        flash("Maaf, mobil ini sudah habis disewa")
        cur.close()
        conn.close()
        return redirect(url_for('sewa'))
    else:
        flash("Permohonan berhasil")

    rental_days = (datetime.strptime(return_date, "%Y-%m-%d") - datetime.strptime(rental_date, "%Y-%m-%d")).days
    total_price = rental_days * car["price_per_day"]

    cur.execute("""
        INSERT INTO rentals (user_id, car_id, rental_date, return_date, total_price, status)
        VALUES (%s, %s, %s, %s, %s, 'pending')
    """, (user_id, car_id, rental_date, return_date, total_price))

    cur.execute("""
        UPDATE cars SET stock = stock - 1 WHERE car_id = %s
    """, (car_id,))

    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for("sewa"))

@app.route("/rental_history")
def rental_history():
    if not session.get("user_id"):
        return redirect(url_for("sign_in"))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    username_filter = request.args.get("username", "").strip()

    if session.get("role") == "admin":
        if username_filter:
            cur.execute("""
                SELECT users.username, rentals.rental_date, rentals.return_date, 
                       rentals.total_price, rentals.status, cars.name AS car_name 
                FROM rentals 
                JOIN cars ON rentals.car_id = cars.car_id
                JOIN users ON rentals.user_id = users.user_id
                WHERE users.username LIKE %s
            """, ('%' + username_filter + '%',))
        else:
            cur.execute("""
                SELECT users.username, rentals.rental_date, rentals.return_date, 
                       rentals.total_price, rentals.status, cars.name AS car_name 
                FROM rentals 
                JOIN cars ON rentals.car_id = cars.car_id
                JOIN users ON rentals.user_id = users.user_id
            """)
    else:
        cur.execute("""
            SELECT users.username, rentals.rental_date, rentals.return_date, 
                   rentals.total_price, rentals.status, cars.name AS car_name 
            FROM rentals 
            JOIN cars ON rentals.car_id = cars.car_id
            JOIN users ON rentals.user_id = users.user_id
            WHERE rentals.user_id = %s
        """, (session["user_id"],))

    history = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("rental_history.html", history=history, role=session["role"])

@app.route("/rental_approval", methods=["GET", "POST"])
def rent_approval():
    if session.get("role") != "admin":
        return redirect(url_for("home"))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    if request.method == "POST":
        rental_id = request.form.get("rental_id")
        action = request.form.get("action")

        if action == "approve":
            cur.execute("UPDATE rentals SET status = 'approved' WHERE rental_id = %s", (rental_id,))
            flash("Penyewaan disetujui!", "success")

        elif action == "reject":
            cur.execute("SELECT car_id FROM rentals WHERE rental_id = %s", (rental_id,))
            result = cur.fetchone()

            if result:
                car_id = result["car_id"]
                cur.execute("UPDATE rentals SET status = 'rejected' WHERE rental_id = %s", (rental_id,))
                cur.execute("UPDATE cars SET stock = stock + 1 WHERE car_id = %s", (car_id,))
                flash("Penyewaan ditolak dan stok mobil dikembalikan!", "danger")
            else:
                flash("Rental tidak ditemukan!", "danger")

        conn.commit()
    cur.execute("""
        SELECT rentals.rental_id, users.username, cars.name AS car_name, rentals.rental_date, rentals.return_date, 
               rentals.total_price, rentals.status 
        FROM rentals 
        JOIN users ON rentals.user_id = users.user_id
        JOIN cars ON rentals.car_id = cars.car_id
        WHERE rentals.status = 'pending'
    """)
    pending_rentals = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("rent_approval.html", pending_rentals=pending_rentals)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
