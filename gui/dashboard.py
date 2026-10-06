import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Allow importing database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import get_services, search_services, add_service, get_connection, save_monitoring_result
from monitoring.monitor import check_service
from reports.html_report import generate_html_report


class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("ServicePulse - Dashboard")
        self.root.geometry("1000x650")
        self.root.resizable(True, True)

        self.create_header()
        self.create_statistics()
        self.create_search()
        self.create_service_table()

        self.load_services()
        self.auto_refresh()

    def auto_refresh(self):
        self.load_services()
        self.root.after(5000, self.auto_refresh)

    # ---------------------------------------------------------
    # HEADER
    # ---------------------------------------------------------
    def create_header(self):
        header = tk.Frame(self.root, bg="#1f2937", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="SERVICEPULSE",
            font=("Arial", 24, "bold"),
            bg="#1f2937",
            fg="white"
        )
        title.pack(side="left", padx=25)

        subtitle = tk.Label(
            header,
            text="Service Monitoring Dashboard",
            font=("Arial", 11),
            bg="#1f2937",
            fg="white"
        )
        subtitle.pack(side="left", padx=10)

    # ---------------------------------------------------------
    # STATISTICS CARDS
    # ---------------------------------------------------------
    def create_statistics(self):
        stats_frame = tk.Frame(self.root)
        stats_frame.pack(fill="x", padx=20, pady=20)

        # Total Services
        total_frame = tk.LabelFrame(stats_frame, text="Total Services", font=("Arial", 11, "bold"))
        total_frame.pack(side="left", expand=True, fill="both", padx=5)
        self.total_label = tk.Label(total_frame, text="0", font=("Arial", 24, "bold"))
        self.total_label.pack(pady=15)

        # UP
        up_frame = tk.LabelFrame(stats_frame, text="UP", font=("Arial", 11, "bold"))
        up_frame.pack(side="left", expand=True, fill="both", padx=5)
        self.up_label = tk.Label(up_frame, text="0", font=("Arial", 24, "bold"), fg="#28a745")
        self.up_label.pack(pady=15)

        # DOWN
        down_frame = tk.LabelFrame(stats_frame, text="DOWN", font=("Arial", 11, "bold"))
        down_frame.pack(side="left", expand=True, fill="both", padx=5)
        self.down_label = tk.Label(down_frame, text="0", font=("Arial", 24, "bold"), fg="#dc3545")
        self.down_label.pack(pady=15)

    # ---------------------------------------------------------
    # SEARCH BAR
    # ---------------------------------------------------------
    def create_search(self):
        search_frame = tk.Frame(self.root)
        search_frame.pack(fill="x", padx=20, pady=5)

        search_label = tk.Label(search_frame, text="Search:", font=("Arial", 11))
        search_label.pack(side="left")

        self.search_entry = tk.Entry(search_frame, width=40, font=("Arial", 11))
        self.search_entry.pack(side="left", padx=10)

        search_button = tk.Button(search_frame, text="Search", command=self.search)
        search_button.pack(side="left")

        refresh_button = tk.Button(search_frame, text="Refresh All", command=self.load_services)
        refresh_button.pack(side="left", padx=10)

    # ---------------------------------------------------------
    # SERVICE TABLE
    # ---------------------------------------------------------
    def create_service_table(self):
        table_frame = tk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        columns = ("id", "service", "url", "status", "response")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.tree.heading("id", text="ID")
        self.tree.heading("service", text="Service")
        self.tree.heading("url", text="URL")
        self.tree.heading("status", text="Status")
        self.tree.heading("response", text="Response Time")

        self.tree.column("id", width=50)
        self.tree.column("service", width=180)
        self.tree.column("url", width=300)
        self.tree.column("status", width=100)
        self.tree.column("response", width=120)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # ---------------------------------------------------------
    # LOAD SERVICES
    # ---------------------------------------------------------
    def load_services(self):
        # Remove existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        services = get_services()
        total = len(services)
        up = 0
        down = 0

        for service in services:
            service_id = service[0]
            service_name = service[1]
            url = service[2]

            status = "UNKNOWN"
            response_time = "-"

            try:
                from database.db import get_history
                history = get_history(service_id)

                if history:
                    latest = history[0]
                    status = latest[3]

                    if latest[5] is not None:
                        response_time = f"{latest[5]:.0f} ms"

                    if status == "UP":
                        up += 1
                    elif status == "DOWN":
                        down += 1
            except Exception:
                pass

            self.tree.insert("", "end", values=(service_id, service_name, url, status, response_time))

        self.total_label.config(text=str(total))
        self.up_label.config(text=str(up))
        self.down_label.config(text=str(down))


    # ---------------------------------------------------------
    # SEARCH & ON-DEMAND PING
    # ---------------------------------------------------------
    def search(self):
        keyword = self.search_entry.get().strip()

        if keyword == "":
            self.load_services()
            return

        services = search_services(keyword)

        # If not found in DB but looks like a URL, add and ping it live
        if not services and (keyword.startswith("http://") or keyword.startswith("https://")):
            try:
                # 1. Clean up domain for the name (e.g. github.com)
                domain_name = keyword.split("//")[-1].split("/")[0].replace("www.", "").capitalize()
                
                # 2. Add to database
                add_service(domain_name, keyword)
                
                # 3. Retrieve new ID
                conn = get_connection()
                cur = conn.cursor()
                cur.execute("SELECT service_id FROM services WHERE url = ?", (keyword,))
                row = cur.fetchone()
                conn.close()
                
                if row:
                    svc_id = row[0]
                    
                    # 4. Ping the network live
                    result = check_service(keyword)
                    
                    # 5. Save to database
                    save_monitoring_result(
                        service_id=svc_id,
                        status=result["status"],
                        status_code=result["status_code"],
                        response_time=result["response_time"]
                    )
                    
                    # 6. Update HTML Report in the background
                    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    db_path = os.path.join(base_dir, 'database', 'servicepulse.db')
                    generate_html_report(db_path=db_path)
                    
                    # 7. Fetch the newly saved service for the GUI table
                    services = search_services(keyword)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to test live URL: {e}")

        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)

        for service in services:
            service_id = service[0]
            service_name = service[1]
            url = service[2]

            status = "UNKNOWN"
            response_time = "-"

            try:
                from database.db import get_history
                history = get_history(service_id)

                if history:
                    latest = history[0]
                    status = latest[3]
                    if latest[5] is not None:
                        response_time = f"{latest[5]:.0f} ms"
            except Exception:
                pass

            self.tree.insert("", "end", values=(service_id, service_name, url, status, response_time))


# ---------------------------------------------------------
# RUN DASHBOARD DIRECTLY
# ---------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = Dashboard(root)
    root.mainloop()