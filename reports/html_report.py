import sqlite3
import os
from datetime import datetime
from analytics.statistics import get_service_statistics

def generate_html_report(db_path, output_dir="reports"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT service_id, service_name, url FROM services')
    services = cursor.fetchall()
    
    total_services = len(services)
    healthy_services = 0
    service_rows = ""
    
    for svc in services:
        svc_id, name, url = svc
        
        cursor.execute('''
            SELECT status, response_time, checked_at FROM monitoring_logs 
            WHERE service_id = ? 
            ORDER BY checked_at DESC LIMIT 1
        ''', (svc_id,))
        latest_log = cursor.fetchone()
        
        stats = get_service_statistics(svc_id, db_path)
        
        if latest_log:
            status, resp_time, last_checked = latest_log
            if status.upper() == "UP":
                healthy_services += 1
                status_color = "#28a745"
            else:
                status_color = "#dc3545"
        else:
            status, resp_time, last_checked = ("UNKNOWN", "N/A", "Never")
            status_color = "#6c757d"
            
        service_rows += f"""
        <tr>
            <td><strong>{name}</strong></td>
            <td><a href="{url}" target="_blank">{url}</a></td>
            <td style="color: {status_color}; font-weight: bold;">{status}</td>
            <td>{resp_time} ms</td>
            <td>{stats['uptime']}%</td>
            <td>{last_checked}</td>
        </tr>
        """
        
    conn.close()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ServicePulse Analytics Report</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f8f9fa; color: #333; }}
            .container {{ max-width: 1000px; margin: auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
            h2 {{ color: #007BFF; border-bottom: 2px solid #007BFF; padding-bottom: 10px; }}
            .summary-cards {{ display: flex; gap: 20px; margin-bottom: 30px; }}
            .card {{ background: #e9ecef; padding: 20px; border-radius: 6px; flex: 1; text-align: center; }}
            .card h3 {{ margin: 0; font-size: 2em; color: #007BFF; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #dee2e6; }}
            th {{ background-color: #f1f3f5; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>ServicePulse System Report</h2>
            <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            
            <div class="summary-cards">
                <div class="card">
                    <h3>{total_services}</h3>
                    <p>Total Monitored Services</p>
                </div>
                <div class="card">
                    <h3 style="color: #28a745;">{healthy_services}</h3>
                    <p>Currently UP</p>
                </div>
                <div class="card">
                    <h3 style="color: #dc3545;">{total_services - healthy_services}</h3>
                    <p>Currently DOWN</p>
                </div>
            </div>
            
            <table>
                <thead>
                    <tr>
                        <th>Service Name</th>
                        <th>URL</th>
                        <th>Current Status</th>
                        <th>Response Time</th>
                        <th>Overall Uptime</th>
                        <th>Last Checked</th>
                    </tr>
                </thead>
                <tbody>
                    {service_rows}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    
    os.makedirs(output_dir, exist_ok=True)
    report_path = os.path.join(output_dir, "index.html")
    
    with open(report_path, "w", encoding="utf-8") as file:
        file.write(html_content)
        
    return report_path

if __name__ == "__main__":
    # Define the path to the database since your function requires it
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Point directly to the root folder where the database is located
    DB_PATH = os.path.join(BASE_DIR, 'servicepulse.db')
    
    # Call the function
    print("Generating report...")
    output_file = generate_html_report(db_path=DB_PATH)
    print(f"Success! Report saved to {output_file}")