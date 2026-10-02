import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'servicepulse.db')

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Clear out any old test data just in case
cursor.execute('DELETE FROM monitoring_logs')
cursor.execute('DELETE FROM services')

# 1. Insert dummy websites
cursor.execute("INSERT INTO services (service_name, url) VALUES ('Google', 'https://google.com')")
cursor.execute("INSERT INTO services (service_name, url) VALUES ('VIT Portal', 'https://vtop.vitbhopal.ac.in')")
cursor.execute("INSERT INTO services (service_name, url) VALUES ('GitHub API', 'https://api.github.com')")

# 2. Insert dummy monitoring logs (simulating network pings)
# Google (100% UP)
cursor.execute("INSERT INTO monitoring_logs (service_id, status, response_time) VALUES (1, 'UP', 142)")
cursor.execute("INSERT INTO monitoring_logs (service_id, status, response_time) VALUES (1, 'UP', 135)")

# VIT Portal (DOWN)
cursor.execute("INSERT INTO monitoring_logs (service_id, status, response_time) VALUES (2, 'DOWN', 0)")

# GitHub (UP)
cursor.execute("INSERT INTO monitoring_logs (service_id, status, response_time) VALUES (3, 'UP', 210)")

conn.commit()
conn.close()

print("Dummy data successfully injected into servicepulse.db!")