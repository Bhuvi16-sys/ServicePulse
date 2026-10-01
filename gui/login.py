import tkinter as tk
from tkinter import messagebox
import sys
import os

# Allow importing dashboard.py
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from gui.dashboard import Dashboard


class LoginWindow:

    def __init__(self, root):

        self.root = root

        self.root.title("ServicePulse - Login")
        self.root.geometry("450x400")
        self.root.resizable(False, False)

        self.create_login_ui()

    # ---------------------------------------------------------
    # LOGIN UI
    # ---------------------------------------------------------

    def create_login_ui(self):

        # Main container
        main_frame = tk.Frame(self.root)

        main_frame.pack(
            expand=True,
            fill="both",
            padx=40,
            pady=30
        )

        # Application title
        title = tk.Label(
            main_frame,
            text="SERVICEPULSE",
            font=("Arial", 26, "bold")
        )

        title.pack(pady=(10, 5))

        subtitle = tk.Label(
            main_frame,
            text="Service Monitoring System",
            font=("Arial", 11)
        )

        subtitle.pack(pady=(0, 30))

        # Username
        username_label = tk.Label(
            main_frame,
            text="Username",
            font=("Arial", 11, "bold")
        )

        username_label.pack(
            anchor="w"
        )

        self.username_entry = tk.Entry(
            main_frame,
            font=("Arial", 12)
        )

        self.username_entry.pack(
            fill="x",
            pady=(5, 15)
        )

        # Password
        password_label = tk.Label(
            main_frame,
            text="Password",
            font=("Arial", 11, "bold")
        )

        password_label.pack(
            anchor="w"
        )

        self.password_entry = tk.Entry(
            main_frame,
            font=("Arial", 12),
            show="*"
        )

        self.password_entry.pack(
            fill="x",
            pady=(5, 20)
        )

        # Login button
        login_button = tk.Button(
            main_frame,
            text="LOGIN",
            font=("Arial", 11, "bold"),
            width=15,
            command=self.login
        )

        login_button.pack(
            pady=10
        )

        # Exit button
        exit_button = tk.Button(
            main_frame,
            text="EXIT",
            width=15,
            command=self.root.destroy
        )

        exit_button.pack(
            pady=5
        )

        # Press Enter to login
        self.root.bind(
            "<Return>",
            lambda event: self.login()
        )

    # ---------------------------------------------------------
    # LOGIN LOGIC
    # ---------------------------------------------------------

    def login(self):

        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        # Temporary credentials
        #
        # We will connect this to the project's
        # actual user database later.

        if username == "admin" and password == "admin":

            messagebox.showinfo(
                "Login Successful",
                "Welcome to ServicePulse!"
            )

            self.open_dashboard()

        elif username == "" or password == "":

            messagebox.showwarning(
                "Missing Information",
                "Please enter username and password."
            )

        else:

            messagebox.showerror(
                "Login Failed",
                "Invalid username or password."
            )

    # ---------------------------------------------------------
    # OPEN DASHBOARD
    # ---------------------------------------------------------

    def open_dashboard(self):

        # Remove login window
        self.root.destroy()

        # Create dashboard window
        dashboard_root = tk.Tk()

        Dashboard(dashboard_root)

        dashboard_root.mainloop()


# -------------------------------------------------------------
# RUN LOGIN
# -------------------------------------------------------------

if __name__ == "__main__":

    root = tk.Tk()

    app = LoginWindow(root)

    root.mainloop()
