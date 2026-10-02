import tkinter as tk
import sqlite3
import sys
import os
import threading

# 1. Path Configuration
# Ensures Python can find all the folders (gui, database, analytics, etc.)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# 2. Import Member 1's GUI
try:
    from gui.dashboard import Dashboard
except ImportError as e:
    print(f"GUI Import Error: {e}")
    print("Ensure Member 1's gui/dashboard.py has a 'Dashboard' class.")

def initialize_database():
    """
    Acts as a safety net for Member 3's database. 
    It ensures the tables exist before the GUI or Analytics try to read them.
    """
    db_path = os.path.join(BASE_DIR, 'servicepulse.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Member 3's schema
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
    
    conn.commit()
    conn.close()

def main():
    print("Initializing ServicePulse Database...")
    initialize_database()
    
    # Note for Member 2 (Monitoring Engine):
    # Their continuous pinging script would be started here as a background thread
    # e.g., threading.Thread(target=start_monitoring_loop, daemon=True).start()
    
    print("Launching ServicePulse GUI...")
    root = tk.Tk()
    
    # Configure the main window properties
    root.geometry("900x600")
    
    # Initialize Member 1's Dashboard
    try:
        app = Dashboard(root)
    except NameError:
        print("Dashboard failed to load. Check the GUI files.")
        
    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()