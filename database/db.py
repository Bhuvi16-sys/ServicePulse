import sqlite3

DB_NAME = "servicepulse.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS services (
        service_id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_name TEXT NOT NULL,
        url TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS monitoring_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_id INTEGER NOT NULL,
        checked_at TEXT DEFAULT CURRENT_TIMESTAMP,
        status TEXT NOT NULL,
        status_code INTEGER,
        response_time REAL,
        FOREIGN KEY (service_id) REFERENCES services(service_id)
    )
    """)

    conn.commit()
    conn.close()


def add_service(service_name, url):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO services (service_name, url) VALUES (?, ?)",
        (service_name, url)
    )

    conn.commit()
    conn.close()


def delete_service(service_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM monitoring_logs WHERE service_id = ?",
        (service_id,)
    )

    cursor.execute(
        "DELETE FROM services WHERE service_id = ?",
        (service_id,)
    )

    conn.commit()
    conn.close()


def update_service(service_id, service_name, url):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE services SET service_name = ?, url = ? WHERE service_id = ?",
        (service_name, url, service_id)
    )

    conn.commit()
    conn.close()


def get_services():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM services")
    services = cursor.fetchall()

    conn.close()
    return services


def save_monitoring_result(service_id, status, status_code, response_time):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO monitoring_logs
        (service_id, status, status_code, response_time)
        VALUES (?, ?, ?, ?)
    """, (service_id, status, status_code, response_time))

    conn.commit()
    conn.close()


def get_history(service_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM monitoring_logs
        WHERE service_id = ?
        ORDER BY checked_at DESC
    """, (service_id,))

    history = cursor.fetchall()

    conn.close()
    return history


def search_services(keyword):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM services
        WHERE service_name LIKE ? OR url LIKE ?
    """, (f"%{keyword}%", f"%{keyword}%"))

    services = cursor.fetchall()

    conn.close()
    return services
