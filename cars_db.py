import mysql.connector
from mysql.connector import errorcode

config = {
    'user': 'admin',
    'password': 'proyekaws2606',  # ganti sesuai password MySQL kamu
    'host': 'database-1.c7wec4ugoiuo.us-east-1.rds.amazonaws.com
}

try:
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()

    # Buat database jika belum ada
    #cursor.execute("DROP DATABASE IF EXISTS car_rental_dbs")
    #print("Database 'car_rental_dbs' telah dihapus jika ada.")
    cursor.execute("CREATE DATABASE IF NOT EXISTS car_rental_dbs")
    print("Database 'car_rental_dbs' berhasil dibuat atau sudah ada.")

    cursor.execute("USE car_rental_dbs")

    # Tabel users
    create_users_table = """
    CREATE TABLE IF NOT EXISTS users (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(150) NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        phone_number VARCHAR(20) NOT NULL,
        role ENUM('member', 'admin') NOT NULL DEFAULT 'member',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """
    cursor.execute(create_users_table)
    print("Tabel 'users' berhasil dibuat.")

    # Password admin dalam plaintext
    admin_password = "admin123"

    # Tabel cars
    create_cars_table = """
    CREATE TABLE IF NOT EXISTS cars (
        car_id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        brand VARCHAR(50) NOT NULL,
        capacity INT NOT NULL,
        fuel_consumption VARCHAR(20),
        cargo VARCHAR(50),
        price_per_day DECIMAL(10,2) NOT NULL,
        stock INT NOT NULL,
        image_path TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB;
    """
    cursor.execute(create_cars_table)
    print("Tabel 'cars' berhasil dibuat.")

    # Tabel rentals
    create_rentals_table = """
    CREATE TABLE IF NOT EXISTS rentals (
        rental_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        car_id INT,
        rental_date DATE NOT NULL,
        return_date DATE NOT NULL,
        total_price DECIMAL(10,2) NOT NULL,
        status ENUM('pending', 'approved', 'rejected') NOT NULL DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
        FOREIGN KEY (car_id) REFERENCES cars(car_id) ON DELETE CASCADE
    ) ENGINE=InnoDB;
    """
    cursor.execute(create_rentals_table)
    print("Tabel 'rentals' berhasil dibuat.")

    # Insert data admin, cek dulu apakah sudah ada
    cursor.execute("SELECT COUNT(*) FROM users WHERE email = %s", ("admin@carrental.com",))
    admin_exists = cursor.fetchone()[0]

    if admin_exists == 0:
        insert_users_query = """
        INSERT INTO users (username, email, password, phone_number, role)
        VALUES (%s, %s, %s, %s, %s)
        """
        users_data = [
            ("Admin", "admin@carrental.com", "admin123", "08123456789", "admin"),
        ]
        cursor.executemany(insert_users_query, users_data)
        cnx.commit()
        print("Data admin berhasil dimasukkan ke tabel 'users'.")
    else:
        print("Data admin sudah ada, tidak perlu ditambahkan.")

    # Insert data mobil jika belum ada
    cursor.execute("SELECT COUNT(*) FROM cars")
    car_count = cursor.fetchone()[0]

    if car_count == 0:
        insert_cars_query = """
        INSERT INTO cars (name, brand, capacity, fuel_consumption, cargo, price_per_day, stock, image_path)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cars_data = [
            ("Toyota Fortuner", "Toyota", 7, "19 liter", "3 koper besar", 600000.00, 5, "images/Fortuner.png"),
            ("Honda CR-V", "Honda", 5, "18 liter", "2 koper besar", 650000.00, 3, "images/Honda CR-V.png"),
            ("Mitsubishi Pajero", "Mitsubishi", 7, "20 liter", "4 koper besar", 800000.00, 1, "images/Mitsubishi pajero.png"),
            ("Toyota Camry", "Toyota", 5, "18 liter", "2 koper besar", 500000.00, 4, "images/Toyota Camry.png"),
            ("Honda Accord", "Honda", 5, "17 liter", "2 koper sedang", 520000.00, 3, "images/Honda Accord.png"),
            ("Mercedes-Benz C-Class", "Mercedes-Benz", 4, "20 liter", "1 koper besar", 700000.00, 2, "images/Mercedes-Benz C-Class.png"),
            ("Daihatsu Ayla", "Daihatsu", 5, "16 liter", "1 koper besar", 300000.00, 5, "images/Daihatsu Ayla.png"),
            ("Toyota Agya", "Toyota", 5, "15 liter", "1 koper sedang", 320000.00, 4, "images/Toyota Agya.png"),
            ("Honda Jazz", "Honda", 4, "14 liter", "1 koper kecil", 350000.00, 3, "images/Honda Jazz.png")
        ]
        cursor.executemany(insert_cars_query, cars_data)
        cnx.commit()
        print("Data mobil berhasil dimasukkan ke tabel 'cars'.")
    else:
        print("Data mobil sudah ada, tidak perlu menambahkan lagi.")

    cursor.close()
    cnx.close()
    print("Proses selesai!")

except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Username atau password salah.")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database tidak ditemukan.")
    else:
        print(f"Terjadi kesalahan: {err}")
