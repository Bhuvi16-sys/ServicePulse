import tkinter as tk
from tkinter import messagebox
import sys
import os

# Allow importing database module
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from database.db import add_service


class ServiceForm:

    def __init__(self, root):

        self.root = root

        self.root.title("ServicePulse - Add Service")
        self.root.geometry("500x450")
        self.root.resizable(False, False)

        self.create_form()

    # ---------------------------------------------------------
    # CREATE FORM
    # ---------------------------------------------------------

    def create_form(self):

        main_frame = tk.Frame(self.root)

        main_frame.pack(
            fill="both",
            expand=True,
            padx=40,
            pady=30
        )

        # Title
        title = tk.Label(
            main_frame,
            text="ADD NEW SERVICE",
            font=("Arial", 22, "bold")
        )

        title.pack(pady=(0, 25))

        # -----------------------------------------------------
        # SERVICE NAME
        # -----------------------------------------------------

        name_label = tk.Label(
            main_frame,
            text="Service Name",
            font=("Arial", 11, "bold")
        )

        name_label.pack(anchor="w")

        self.name_entry = tk.Entry(
            main_frame,
            font=("Arial", 12)
        )

        self.name_entry.pack(
            fill="x",
            pady=(5, 15)
        )

        # -----------------------------------------------------
        # URL
        # -----------------------------------------------------

        url_label = tk.Label(
            main_frame,
            text="Service URL",
            font=("Arial", 11, "bold")
        )

        url_label.pack(anchor="w")

        self.url_entry = tk.Entry(
            main_frame,
            font=("Arial", 12)
        )

        self.url_entry.pack(
            fill="x",
            pady=(5, 15)
        )

        # -----------------------------------------------------
        # CHECK INTERVAL
        # -----------------------------------------------------

        interval_label = tk.Label(
            main_frame,
            text="Check Interval (seconds)",
            font=("Arial", 11, "bold")
        )

        interval_label.pack(anchor="w")

        self.interval_entry = tk.Entry(
            main_frame,
            font=("Arial", 12)
        )

        self.interval_entry.insert(
            0,
            "60"
        )

        self.interval_entry.pack(
            fill="x",
            pady=(5, 15)
        )

        # -----------------------------------------------------
        # DESCRIPTION
        # -----------------------------------------------------

        description_label = tk.Label(
            main_frame,
            text="Description",
            font=("Arial", 11, "bold")
        )

        description_label.pack(anchor="w")

        self.description_entry = tk.Entry(
            main_frame,
            font=("Arial", 12)
        )

        self.description_entry.pack(
            fill="x",
            pady=(5, 20)
        )

        # -----------------------------------------------------
        # BUTTONS
        # -----------------------------------------------------

        button_frame = tk.Frame(main_frame)

        button_frame.pack()

        add_button = tk.Button(
            button_frame,
            text="ADD SERVICE",
            font=("Arial", 10, "bold"),
            width=15,
            command=self.add_service
        )

        add_button.pack(
            side="left",
            padx=5
        )

        clear_button = tk.Button(
            button_frame,
            text="CLEAR",
            width=15,
            command=self.clear_form
        )

        clear_button.pack(
            side="left",
            padx=5
        )

    # ---------------------------------------------------------
    # ADD SERVICE
    # ---------------------------------------------------------

    def add_service(self):

        name = self.name_entry.get().strip()
        url = self.url_entry.get().strip()
        interval = self.interval_entry.get().strip()
        description = self.description_entry.get().strip()

        # Validate service name
        if name == "":
            messagebox.showwarning(
                "Missing Information",
                "Please enter a service name."
            )
            self.name_entry.focus()
            return

        # Validate URL
        if url == "":
            messagebox.showwarning(
                "Missing Information",
                "Please enter the service URL."
            )
            self.url_entry.focus()
            return

        # Validate interval
        try:

            interval = int(interval)

            if interval <= 0:
                raise ValueError

        except ValueError:

            messagebox.showerror(
                "Invalid Interval",
                "Check interval must be a positive number."
            )

            self.interval_entry.focus()

            return

        # -----------------------------------------------------
        # SAVE TO DATABASE
        # -----------------------------------------------------

        try:

            add_service(
                name,
                url,
                interval,
                description
            )

            messagebox.showinfo(
                "Success",
                f"Service '{name}' added successfully."
            )

            self.clear_form()

        except Exception as e:

            messagebox.showerror(
                "Database Error",
                f"Could not add service.\n\n{e}"
            )

    # ---------------------------------------------------------
    # CLEAR FORM
    # ---------------------------------------------------------

    def clear_form(self):

        self.name_entry.delete(
            0,
            tk.END
        )

        self.url_entry.delete(
            0,
            tk.END
        )

        self.interval_entry.delete(
            0,
            tk.END
        )

        self.interval_entry.insert(
            0,
            "60"
        )

        self.description_entry.delete(
            0,
            tk.END

        )

        self.name_entry.focus()


# -------------------------------------------------------------
# RUN DIRECTLY
# -------------------------------------------------------------

if __name__ == "__main__":

    root = tk.Tk()

    app = ServiceForm(root)

    root.mainloop()
