import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database', 'servicepulse.db')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. Create tables in case they don't exist yet
cursor.execute('''
CREATE TABLE IF NOT EXISTS services (
    service_id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_name TEXT NOT NULL,
    url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS monitoring_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT,
    response_time INTEGER,
    FOREIGN KEY(service_id) REFERENCES services(service_id)
)
''')

# 2. Clear out any existing rows to prevent duplicates
cursor.execute('DELETE FROM monitoring_logs')
cursor.execute('DELETE FROM services')

# 3. Insert dummy websites
cursor.execute("INSERT INTO services (service_name, url) VALUES ('Google', 'https://google.com')")
cursor.execute("INSERT INTO services (service_name, url) VALUES ('VIT Portal', 'https://vtop.vitbhopal.ac.in')")

# 4. Insert dummy monitoring logs
cursor.execute("INSERT INTO monitoring_logs (service_id, status, response_time) VALUES (1, 'UP', 142)")
cursor.execute("INSERT INTO monitoring_logs (service_id, status, response_time) VALUES (1, 'UP', 135)")
cursor.execute("INSERT INTO monitoring_logs (service_id, status, response_time) VALUES (2, 'DOWN', 0)")

conn.commit()
conn.close()

print("Success! Tables created and dummy data injected into database/servicepulse.db")