import sqlite3
import os

# Dynamically resolve the database path based on the folder structure
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, 'database', 'servicepulse.db')

def get_service_statistics(service_id, db_path=DEFAULT_DB_PATH):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT status, response_time 
            FROM monitoring_logs 
            WHERE service_id = ?
        ''', (service_id,))
        
        logs = cursor.fetchall()
        conn.close()
        
        if not logs:
            return {"uptime": 0.0, "avg_response": 0, "total_checks": 0, "failed_checks": 0}
        
        total_checks = len(logs)
        failed_checks = sum(1 for log in logs if log[0].upper() == 'DOWN')
        successful_checks = total_checks - failed_checks
        
        uptime = (successful_checks / total_checks) * 100
        
        response_times = [log[1] for log in logs if log[1] is not None and log[0].upper() == 'UP']
        avg_response = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "uptime": round(uptime, 2),
            "avg_response": round(avg_response, 1),
            "total_checks": total_checks,
            "failed_checks": failed_checks
        }
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return {"uptime": 0.0, "avg_response": 0, "total_checks": 0, "failed_checks": 0}