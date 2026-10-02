import sqlite3
import matplotlib.pyplot as plt
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, 'database', 'servicepulse.db')
CHARTS_DIR = os.path.join(BASE_DIR, 'reports', 'charts')

def generate_response_time_graph(service_id, output_filename="response_graph.png", db_path=DEFAULT_DB_PATH):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT checked_at, response_time 
        FROM monitoring_logs 
        WHERE service_id = ? AND status = 'UP'
        ORDER BY checked_at ASC LIMIT 50
    ''', (service_id,))
    
    data = cursor.fetchall()
    
    # Fetch service name for the chart title
    cursor.execute('SELECT service_name FROM services WHERE service_id = ?', (service_id,))
    service_name_row = cursor.fetchone()
    service_name = service_name_row[0] if service_name_row else f"Service {service_id}"
    
    conn.close()
    
    if not data:
        return False
    
    # Extracting just the HH:MM portion for cleaner X-axis labels
    times = [row[0].split(" ")[-1][:5] for row in data] 
    responses = [row[1] for row in data]
    
    plt.figure(figsize=(7, 4))
    plt.plot(times, responses, marker='o', linestyle='-', color='#007BFF', linewidth=2)
    plt.title(f"Response Time Trend: {service_name}")
    plt.xlabel("Time")
    plt.ylabel("Response Time (ms)")
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    os.makedirs(CHARTS_DIR, exist_ok=True)
    final_output_path = os.path.join(CHARTS_DIR, output_filename)
        
    plt.savefig(final_output_path, dpi=100)
    plt.close()
    return final_output_path