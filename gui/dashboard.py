import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import threading
import webbrowser
from datetime import datetime

# Charts are saved as PNG files, so matplotlib must not open its own window
# inside the Tkinter app.
import matplotlib
matplotlib.use("Agg")

# Allow importing database module
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from database.db import (get_services, search_services, add_service, get_connection,
                         save_monitoring_result, get_history)
from monitoring.monitor import check_service
from reports.html_report import generate_html_report
from analytics.charts import generate_response_time_graph

DB_PATH = os.path.join(BASE_DIR, "database", "servicepulse.db")

# ---------------------------------------------------------
# COLOUR PALETTE
# ---------------------------------------------------------
BG = "#f3f4f6"
HEADER_BG = "#111827"
CARD_BG = "#ffffff"
TEXT = "#111827"
MUTED = "#6b7280"
BLUE = "#2563eb"
GREEN = "#16a34a"
RED = "#dc2626"
AMBER = "#d97706"
UP_ROW = "#ecfdf5"
DOWN_ROW = "#fef2f2"


# ---------------------------------------------------------
# HELPERS (statistics from logged history)
# History rows follow the same layout the original dashboard used:
# row[3] = status, row[5] = response time (ms). Newest row first.
# ---------------------------------------------------------
def compute_stats(history):
    total = len(history)
    if total == 0:
        return None
    ups = [r for r in history if r[3] == "UP"]
    times = [r[5] for r in ups if r[5] is not None]
    return {
        "total": total,
        "uptime": len(ups) / total * 100,
        "avg": sum(times) / len(times) if times else None,
        "min": min(times) if times else None,
        "max": max(times) if times else None,
        "last": history[0][3],
    }


def fmt_ms(value):
    return f"{value:.0f} ms" if value is not None else "-"


class Dashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("ServicePulse - Dashboard")
        self.root.geometry("1100x720")
        self.root.minsize(900, 600)
        self.root.configure(bg=BG)

        self._checking = False
        self._check_progress = ""

        self.setup_styles()
        self.create_header()
        self.create_statistics()
        self.create_toolbar()
        self.create_service_table()
        self.create_status_bar()

        self.load_services()

    # ---------------------------------------------------------
    # STYLES
    # ---------------------------------------------------------
    def setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Treeview", font=("Segoe UI", 10), rowheight=30,
                        background=CARD_BG, fieldbackground=CARD_BG, borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"),
                        background="#e5e7eb", foreground=TEXT, relief="flat", padding=6)
        style.map("Treeview", background=[("selected", BLUE)],
                  foreground=[("selected", "white")])
        style.map("Treeview.Heading", background=[("active", "#d1d5db")])

    def make_button(self, parent, text, command, color=BLUE):
        btn = tk.Button(parent, text=text, command=command, bg=color, fg="white",
                        activebackground=color, activeforeground="white",
                        font=("Segoe UI", 10, "bold"), relief="flat", bd=0,
                        padx=14, pady=6, cursor="hand2")
        return btn

    # ---------------------------------------------------------
    # HEADER
    # ---------------------------------------------------------
    def create_header(self):
        header = tk.Frame(self.root, bg=HEADER_BG, height=76)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(header, text="\u25CF", font=("Arial", 22), bg=HEADER_BG,
                 fg=GREEN).pack(side="left", padx=(25, 6))
        tk.Label(header, text="SERVICEPULSE", font=("Segoe UI", 24, "bold"),
                 bg=HEADER_BG, fg="white").pack(side="left")
        tk.Label(header, text="Service Monitoring Dashboard", font=("Segoe UI", 11),
                 bg=HEADER_BG, fg="#9ca3af").pack(side="left", padx=14, pady=(10, 0))

    # ---------------------------------------------------------
    # STATISTICS CARDS
    # ---------------------------------------------------------
    def make_card(self, parent, title, color):
        card = tk.Frame(parent, bg=CARD_BG, highlightbackground="#e5e7eb", highlightthickness=1)
        card.pack(side="left", expand=True, fill="both", padx=6)
        tk.Frame(card, bg=color, width=6).pack(side="left", fill="y")
        body = tk.Frame(card, bg=CARD_BG)
        body.pack(side="left", expand=True, fill="both", padx=14, pady=10)
        tk.Label(body, text=title.upper(), font=("Segoe UI", 9, "bold"),
                 bg=CARD_BG, fg=MUTED).pack(anchor="w")
        value = tk.Label(body, text="0", font=("Segoe UI", 24, "bold"), bg=CARD_BG, fg=color)
        value.pack(anchor="w")
        return value

    def create_statistics(self):
        stats_frame = tk.Frame(self.root, bg=BG)
        stats_frame.pack(fill="x", padx=14, pady=(18, 6))

        self.total_label = self.make_card(stats_frame, "Total Services", BLUE)
        self.up_label = self.make_card(stats_frame, "UP", GREEN)
        self.down_label = self.make_card(stats_frame, "DOWN", RED)
        self.uptime_label = self.make_card(stats_frame, "Overall Uptime", AMBER)
        self.avg_label = self.make_card(stats_frame, "Avg Response", "#7c3aed")

    # ---------------------------------------------------------
    # TOOLBAR (search + actions)
    # ---------------------------------------------------------
    def create_toolbar(self):
        bar = tk.Frame(self.root, bg=BG)
        bar.pack(fill="x", padx=20, pady=(8, 4))

        tk.Label(bar, text="Search:", font=("Segoe UI", 10), bg=BG, fg=TEXT).pack(side="left")
        self.search_entry = tk.Entry(bar, width=30, font=("Segoe UI", 10), relief="solid", bd=1)
        self.search_entry.pack(side="left", padx=8, ipady=3)
        self.search_entry.bind("<Return>", lambda e: self.search())

        self.make_button(bar, "Search", self.search).pack(side="left", padx=3)
        self.make_button(bar, "Refresh All", self.load_services, "#4b5563").pack(side="left", padx=3)

        # Right-hand action buttons
        self.make_button(bar, "Generate Report", self.open_report, GREEN).pack(side="right", padx=3)
        self.make_button(bar, "View Chart & Stats", self.show_details, "#7c3aed").pack(side="right", padx=3)
        self.check_btn = self.make_button(bar, "Check All Now", self.check_all_now, AMBER)
        self.check_btn.pack(side="right", padx=3)
        self.make_button(bar, "+ Add Service", self.add_service_dialog, BLUE).pack(side="right", padx=3)

    # ---------------------------------------------------------
    # SERVICE TABLE
    # ---------------------------------------------------------
    def create_service_table(self):
        table_frame = tk.Frame(self.root, bg=BG)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(6, 4))

        columns = ("id", "service", "url", "status", "response", "uptime")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        headings = {"id": "ID", "service": "Service", "url": "URL",
                    "status": "Status", "response": "Response Time", "uptime": "Uptime"}
        widths = {"id": 50, "service": 170, "url": 300, "status": 90, "response": 120, "uptime": 90}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            anchor = "w" if col in ("service", "url") else "center"
            self.tree.column(col, width=widths[col], anchor=anchor)

        self.tree.tag_configure("up", background=UP_ROW, foreground="#065f46")
        self.tree.tag_configure("down", background=DOWN_ROW, foreground="#991b1b")
        self.tree.tag_configure("unknown", background=CARD_BG, foreground=MUTED)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Double-click a row to open its chart and statistics
        self.tree.bind("<Double-1>", lambda e: self.show_details())

    # ---------------------------------------------------------
    # STATUS BAR
    # ---------------------------------------------------------
    def create_status_bar(self):
        self.status_var = tk.StringVar(value="Ready")
        bar = tk.Label(self.root, textvariable=self.status_var, anchor="w",
                       font=("Segoe UI", 9), bg="#e5e7eb", fg=MUTED, padx=14, pady=4)
        bar.pack(fill="x", side="bottom")

    # ---------------------------------------------------------
    # POPULATE TABLE (shared by load and search)
    # ---------------------------------------------------------
    def populate_table(self, services, update_cards=False):
        for item in self.tree.get_children():
            self.tree.delete(item)

        up = down = 0
        all_ups = all_checks = 0
        up_times = []

        for service in services:
            service_id, service_name, url = service[0], service[1], service[2]
            status, response_time, uptime = "UNKNOWN", "-", "-"

            try:
                history = get_history(service_id)
                if history:
                    latest = history[0]
                    status = latest[3]
                    if latest[5] is not None:
                        response_time = fmt_ms(latest[5])
                        if status == "UP":
                            up_times.append(latest[5])

                    stats = compute_stats(history)
                    if stats:
                        uptime = f"{stats['uptime']:.1f}%"
                        all_checks += stats["total"]
                        all_ups += round(stats["uptime"] * stats["total"] / 100)

                    if status == "UP":
                        up += 1
                    elif status == "DOWN":
                        down += 1
            except Exception:
                pass

            tag = {"UP": "up", "DOWN": "down"}.get(status, "unknown")
            marker = {"UP": "\u25CF UP", "DOWN": "\u25CF DOWN"}.get(status, status)
            self.tree.insert("", "end", values=(service_id, service_name, url, marker,
                                                response_time, uptime), tags=(tag,))

        if update_cards:
            self.total_label.config(text=str(len(services)))
            self.up_label.config(text=str(up))
            self.down_label.config(text=str(down))
            self.uptime_label.config(
                text=f"{all_ups / all_checks * 100:.1f}%" if all_checks else "-")
            self.avg_label.config(
                text=fmt_ms(sum(up_times) / len(up_times)) if up_times else "-")

    # ---------------------------------------------------------
    # LOAD SERVICES
    # ---------------------------------------------------------
    def load_services(self):
        self.populate_table(get_services(), update_cards=True)
        self.search_entry.delete(0, tk.END)
        self.status_var.set(f"Last refreshed: {datetime.now():%Y-%m-%d %H:%M:%S}")

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
                domain_name = keyword.split("//")[-1].split("/")[0].replace("www.", "").capitalize()
                add_service(domain_name, keyword)

                conn = get_connection()
                cur = conn.cursor()
                cur.execute("SELECT service_id FROM services WHERE url = ?", (keyword,))
                row = cur.fetchone()
                conn.close()

                if row:
                    svc_id = row[0]
                    result = check_service(keyword)
                    save_monitoring_result(
                        service_id=svc_id,
                        status=result["status"],
                        status_code=result["status_code"],
                        response_time=result["response_time"]
                    )
                    generate_html_report(db_path=DB_PATH)
                    services = search_services(keyword)

            except Exception as e:
                messagebox.showerror("Error", f"Failed to test live URL: {e}")

        self.populate_table(services)
        self.status_var.set(f"{len(services)} result(s) for '{keyword}'")

    # ---------------------------------------------------------
    # ADD SERVICE DIALOG
    # ---------------------------------------------------------
    def add_service_dialog(self):
        win = tk.Toplevel(self.root)
        win.title("Add Service")
        win.configure(bg=BG)
        win.geometry("420x210")
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="Service name", bg=BG, font=("Segoe UI", 10)).pack(anchor="w", padx=24, pady=(20, 2))
        name_entry = tk.Entry(win, font=("Segoe UI", 10), relief="solid", bd=1)
        name_entry.pack(fill="x", padx=24, ipady=3)

        tk.Label(win, text="URL (https://...)", bg=BG, font=("Segoe UI", 10)).pack(anchor="w", padx=24, pady=(12, 2))
        url_entry = tk.Entry(win, font=("Segoe UI", 10), relief="solid", bd=1)
        url_entry.pack(fill="x", padx=24, ipady=3)

        def save():
            name, url = name_entry.get().strip(), url_entry.get().strip()
            if not name or not url.startswith(("http://", "https://")):
                messagebox.showwarning("Invalid input", "Enter a name and a URL starting with http:// or https://", parent=win)
                return
            try:
                add_service(name, url)
            except Exception as e:
                messagebox.showerror("Error", f"Could not add service: {e}", parent=win)
                return
            win.destroy()
            self.load_services()

        self.make_button(win, "Save", save, GREEN).pack(pady=16)

    # ---------------------------------------------------------
    # CHECK ALL NOW (background thread so the window never freezes)
    # ---------------------------------------------------------
    def check_all_now(self):
        if self._checking:
            return
        services = get_services()
        if not services:
            messagebox.showinfo("No services", "Add a service first.")
            return

        self._checking = True
        self.check_btn.config(state="disabled", text="Checking...")
        threading.Thread(target=self._check_worker, args=(services,), daemon=True).start()
        self.root.after(300, self._poll_check)

    def _check_worker(self, services):
        total = len(services)
        for i, service in enumerate(services, start=1):
            service_id, name, url = service[0], service[1], service[2]
            self._check_progress = f"Checking {name} ({i}/{total})..."
            try:
                result = check_service(url)
                save_monitoring_result(
                    service_id=service_id,
                    status=result["status"],
                    status_code=result["status_code"],
                    response_time=result["response_time"]
                )
            except Exception:
                pass
        try:
            generate_html_report(db_path=DB_PATH)
        except Exception:
            pass
        self._checking = False

    def _poll_check(self):
        if self._checking:
            self.status_var.set(self._check_progress)
            self.root.after(300, self._poll_check)
        else:
            self.check_btn.config(state="normal", text="Check All Now")
            self.load_services()
            self.status_var.set(f"Check complete: {datetime.now():%Y-%m-%d %H:%M:%S}")

    # ---------------------------------------------------------
    # CHART + STATISTICS WINDOW
    # ---------------------------------------------------------
    def selected_service(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select a service", "Click a service row first.")
            return None
        values = self.tree.item(selected[0])["values"]
        return values[0], values[1]  # id, name

    def show_details(self):
        picked = self.selected_service()
        if not picked:
            return
        service_id, name = picked

        win = tk.Toplevel(self.root)
        win.title(f"{name} - Chart & Statistics")
        win.configure(bg=BG)

        tk.Label(win, text=name, font=("Segoe UI", 16, "bold"), bg=BG, fg=TEXT).pack(pady=(14, 6))

        # Statistics chips
        stats = compute_stats(get_history(service_id))
        chips = tk.Frame(win, bg=BG)
        chips.pack(padx=14, pady=4)
        if stats:
            items = [
                ("Uptime", f"{stats['uptime']:.1f}%", AMBER),
                ("Checks", str(stats["total"]), BLUE),
                ("Avg", fmt_ms(stats["avg"]), "#7c3aed"),
                ("Min", fmt_ms(stats["min"]), GREEN),
                ("Max", fmt_ms(stats["max"]), RED),
            ]
            for title, value, color in items:
                chip = tk.Frame(chips, bg=CARD_BG, highlightbackground="#e5e7eb", highlightthickness=1)
                chip.pack(side="left", padx=5)
                tk.Label(chip, text=title.upper(), font=("Segoe UI", 8, "bold"), bg=CARD_BG, fg=MUTED).pack(padx=16, pady=(6, 0))
                tk.Label(chip, text=value, font=("Segoe UI", 14, "bold"), bg=CARD_BG, fg=color).pack(padx=16, pady=(0, 6))
        else:
            tk.Label(chips, text="No monitoring history yet.", bg=BG, fg=MUTED).pack()

        # Chart (PNG produced by analytics/charts.py)
        try:
            path = generate_response_time_graph(service_id)
        except Exception as e:
            path = False
            messagebox.showerror("Chart error", str(e), parent=win)

        if path:
            img = tk.PhotoImage(file=path)
            label = tk.Label(win, image=img, bg=CARD_BG, bd=1, relief="solid")
            label.image = img  # keep a reference or Tk will drop the image
            label.pack(padx=20, pady=12)
        else:
            tk.Label(win, text="No UP checks recorded yet, so there is nothing to plot.",
                     bg=BG, fg=MUTED, font=("Segoe UI", 10)).pack(padx=40, pady=30)

        self.make_button(win, "Close", win.destroy, "#4b5563").pack(pady=(0, 14))

    # ---------------------------------------------------------
    # HTML REPORT
    # ---------------------------------------------------------
    def open_report(self):
        try:
            result = generate_html_report(db_path=DB_PATH)
        except Exception as e:
            messagebox.showerror("Report error", f"Could not generate report: {e}")
            return

        # Use the returned path if the function gives one, otherwise the default file
        candidates = []
        if isinstance(result, str):
            candidates.append(result)
        candidates.append(os.path.join(BASE_DIR, "reports", "index.html"))

        for path in candidates:
            if os.path.exists(path):
                webbrowser.open("file:///" + os.path.abspath(path).replace("\\", "/"))
                self.status_var.set(f"Report opened: {path}")
                return

        messagebox.showinfo("Report generated",
                            "The report was generated, but its file could not be located automatically.\n"
                            "Check the reports folder.")


# ---------------------------------------------------------
# RUN DASHBOARD DIRECTLY
# ---------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = Dashboard(root)
    root.mainloop()
    