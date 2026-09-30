import tkinter as tk
from tkinter import ttk, messagebox
import json
import csv
import os

DATA_FILE = "tracker_data.json"

class AssignmentTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Assignment Tracker")
        self.root.geometry("600x450")
        
        self.records = self.load_data()

        # Widgets
        ttk.Label(root, text="Enrollment:").grid(row=0, column=0, padx=5, pady=5)
        self.ent_enrollment = ttk.Entry(root)
        self.ent_enrollment.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(root, text="Name:").grid(row=1, column=0, padx=5, pady=5)
        self.ent_name = ttk.Entry(root)
        self.ent_name.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(root, text="Assignment:").grid(row=2, column=0, padx=5, pady=5)
        self.ent_assignment = ttk.Entry(root)
        self.ent_assignment.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(root, text="Status:").grid(row=3, column=0, padx=5, pady=5)
        self.status_var = tk.StringVar(value="Completed")
        self.cmb_status = ttk.Combobox(root, textvariable=self.status_var, values=["Pending", "Completed"])
        self.cmb_status.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(root, text="Marks:").grid(row=4, column=0, padx=5, pady=5)
        self.ent_marks = ttk.Entry(root)
        self.ent_marks.grid(row=4, column=1, padx=5, pady=5)

        ttk.Button(root, text="Add/Update Record", command=self.save_record).grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(root, text="Export CSV", command=self.export_csv).grid(row=6, column=0, columnspan=2, pady=5)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        return []

    def save_record(self):
        enrollment = self.ent_enrollment.get().strip()
        name = self.ent_name.get().strip()
        assignment = self.ent_assignment.get().strip()
        status = self.status_var.get()
        marks = self.ent_marks.get().strip()

        if not (enrollment and name and assignment and marks):
            messagebox.showerror("Error", "All fields are required.")
            return

        rec = {
            "enrollment": enrollment,
            "name": name,
            "assignment": assignment,
            "status": status,
            "marks": marks,
            "remarks": "N/A"
        }
        self.records.append(rec)
        with open(DATA_FILE, "w") as f:
            json.dump(self.records, f)
            
        messagebox.showinfo("Success", "Record added successfully!")

    def export_csv(self):
        with open("report.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["enrollment", "name", "assignment", "status", "marks", "remarks"])
            writer.writeheader()
            writer.writerows(self.records)
        messagebox.showinfo("Export", "Exported report.csv successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = AssignmentTrackerApp(root)
    root.mainloop()