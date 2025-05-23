import tkinter as tk
from tkinter import messagebox
import json
import serial
import threading
from datetime import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

CONFIG_FILE = "config.json"

class WeightMeasurementApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weight Measurement System")
        self.data = self.load_config()
        self.serial_port = None
        self.reading = False
        self.create_widgets()

    def load_config(self):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.data, f, indent=4)

    def create_widgets(self):
        self.root.geometry("950x700")  # Wider, shorter window to fit content better

        # --- Line 1: Start/Stop Buttons ---
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=(20, 10), fill='x')
        self.start_button = tk.Button(top_frame, text="START", bg="orange", command=self.start_reading, font=('Arial', 12, 'bold'))
        self.start_button.pack(side=tk.LEFT, padx=20, expand=True, fill='x')
        self.save_button = tk.Button(top_frame, text="STOP", bg="red", command=self.stop_reading, font=('Arial', 12, 'bold'))
        self.save_button.pack(side=tk.LEFT, padx=20, expand=True, fill='x')

        # --- New Section: COM Port and Baud Rate ---
        comms_frame = tk.Frame(self.root)
        comms_frame.pack(fill='x', padx=20, pady=(0, 10))

        tk.Label(comms_frame, text="COM PORT:", font=('Arial', 11, 'bold')).grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.com_port_entry = tk.Entry(comms_frame, font=('Arial', 11), width=15)
        self.com_port_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        self.com_port_entry.insert(0, self.data.get("com_port", "COM6"))

        tk.Label(comms_frame, text="BAUD RATE:", font=('Arial', 11, 'bold')).grid(row=0, column=2, padx=10, pady=5, sticky='e')
        self.baud_rate_entry = tk.Entry(comms_frame, font=('Arial', 11), width=15)
        self.baud_rate_entry.grid(row=0, column=3, padx=10, pady=5, sticky='w')
        self.baud_rate_entry.insert(0, self.data.get("baud_rate", "9600"))

        # --- Separator ---
        tk.Frame(self.root, height=2, bd=1, relief=tk.SUNKEN).pack(fill='x', padx=10, pady=10)

        # --- Line 2: TEST DETAILS Table ---
        details_frame = tk.LabelFrame(self.root, text="TEST DETAILS", font=('Arial', 13, 'bold'), padx=10, pady=10)
        details_frame.pack(fill='x', padx=20, pady=5)

        # Table headers
        headers = ["DATE", "EQUIPMENT NAME", "EQUIPMENT MAKE", "CAPACITY (T)"]
        for i, h in enumerate(headers):
            tk.Label(details_frame, text=h, font=('Arial', 11, 'bold')).grid(row=0, column=i, padx=10, pady=5, sticky='nsew')

        # Table entries
        self.date_entry = tk.Entry(details_frame, font=('Arial', 11))
        self.date_entry.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')
        self.date_entry.insert(0, self.data.get("date", datetime.today().strftime('%Y-%m-%d')))
        self.date_entry.bind("<FocusIn>", self.set_date_to_today)
        self.date_entry.bind("<KeyRelease>", lambda e: self.update_data("date", self.date_entry.get()))

        self.name_entry = tk.Entry(details_frame, font=('Arial', 11))
        self.name_entry.grid(row=1, column=1, padx=10, pady=5, sticky='nsew')
        self.name_entry.insert(0, self.data.get("equipment_name", ""))
        self.name_entry.bind("<KeyRelease>", lambda e: self.update_data("equipment_name", self.name_entry.get()))

        self.make_entry = tk.Entry(details_frame, font=('Arial', 11))
        self.make_entry.grid(row=1, column=2, padx=10, pady=5, sticky='nsew')
        self.make_entry.insert(0, self.data.get("equipment_make", ""))
        self.make_entry.bind("<KeyRelease>", lambda e: self.update_data("equipment_make", self.make_entry.get()))

        self.capacity_entry = tk.Entry(details_frame, font=('Arial', 11))
        self.capacity_entry.grid(row=1, column=3, padx=10, pady=5, sticky='nsew')
        self.capacity_entry.insert(0, str(self.data.get("capacity_t", "")))
        self.capacity_entry.bind("<KeyRelease>", lambda e: self.update_data("capacity_t", self.capacity_entry.get()))

        # --- Separator ---
        tk.Frame(self.root, height=2, bd=1, relief=tk.SUNKEN).pack(fill='x', padx=10, pady=10)

        # --- Line 3: TEST RESULT Table ---
        result_frame = tk.LabelFrame(self.root, text="TEST RESULT", font=('Arial', 13, 'bold'), padx=10, pady=10)
        result_frame.pack(fill='x', padx=20, pady=5)

        result_headers = ["TEST LOAD (T)", "Load Cell Value", "DURATION (s)", "Timer"]
        for i, h in enumerate(result_headers):
            tk.Label(result_frame, text=h, font=('Arial', 11, 'bold')).grid(row=0, column=i, padx=10, pady=5, sticky='nsew')

        self.test_load_entry = tk.Entry(result_frame, font=('Arial', 11))
        self.test_load_entry.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')

        self.load_cell_value = tk.Entry(result_frame, font=('Arial', 11))
        self.load_cell_value.grid(row=1, column=1, padx=10, pady=5, sticky='nsew')

        self.duration_entry = tk.Entry(result_frame, font=('Arial', 11))
        self.duration_entry.grid(row=1, column=2, padx=10, pady=5, sticky='nsew')

        self.timer_label = tk.Label(result_frame, text="00:00", font=('Arial', 11))
        self.timer_label.grid(row=1, column=3, padx=10, pady=5, sticky='nsew')

        # --- Separator ---
        tk.Frame(self.root, height=2, bd=1, relief=tk.SUNKEN).pack(fill='x', padx=10, pady=10)

        # --- Line 4: RESULT ---
        result_status_frame = tk.LabelFrame(self.root, text="RESULT", font=('Arial', 13, 'bold'), padx=10, pady=10)
        result_status_frame.pack(fill='x', padx=20, pady=5)
        tk.Label(result_status_frame, text="RESULT :", font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=10)
        self.result_label = tk.Label(result_status_frame, text="Pending", font=('Arial', 12, 'bold'), bg="lightgray", width=25)
        self.result_label.pack(side=tk.LEFT, padx=10)

        # --- Separator ---
        tk.Frame(self.root, height=2, bd=1, relief=tk.SUNKEN).pack(fill='x', padx=10, pady=10)

        # --- Line 5: CONDUCTED BY / APPROVED BY Table ---
        ca_frame = tk.LabelFrame(self.root, text="CONDUCTED BY / APPROVED BY", font=('Arial', 13, 'bold'), padx=10, pady=10)
        ca_frame.pack(fill='x', padx=20, pady=5)

        ca_headers = ["CONDUCTED BY NAME", "CONDUCTED BY DESIGNATION", "APPROVED BY NAME", "APPROVED BY DESIGNATION"]
        for i, h in enumerate(ca_headers):
            tk.Label(ca_frame, text=h, font=('Arial', 11, 'bold')).grid(row=0, column=i, padx=10, pady=5, sticky='nsew')

        self.conducted_name_entry = tk.Entry(ca_frame, font=('Arial', 11))
        self.conducted_name_entry.grid(row=1, column=0, padx=10, pady=5, sticky='nsew')
        self.conducted_name_entry.insert(0, self.data.get("conducted_by", {}).get("name", ""))

        self.conducted_designation_entry = tk.Entry(ca_frame, font=('Arial', 11))
        self.conducted_designation_entry.grid(row=1, column=1, padx=10, pady=5, sticky='nsew')
        self.conducted_designation_entry.insert(0, self.data.get("conducted_by", {}).get("designation", ""))

        self.approved_name_entry = tk.Entry(ca_frame, font=('Arial', 11))
        self.approved_name_entry.grid(row=1, column=2, padx=10, pady=5, sticky='nsew')
        self.approved_name_entry.insert(0, self.data.get("approved_by", {}).get("name", ""))

        self.approved_designation_entry = tk.Entry(ca_frame, font=('Arial', 11))
        self.approved_designation_entry.grid(row=1, column=3, padx=10, pady=5, sticky='nsew')
        self.approved_designation_entry.insert(0, self.data.get("approved_by", {}).get("designation", ""))

        # Add Save to PDF button at the bottom
        save_pdf_btn = tk.Button(self.root, text="Save", bg="green", fg="white", font=('Arial', 12, 'bold'), command=self.save_to_pdf)
        save_pdf_btn.pack(pady=10)

    def save_values(self):
        try:
            capacity = float(self.capacity_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Capacity must be a number.")
            return
        self.data = {
            "date": self.date_entry.get(),
            "equipment_name": self.name_entry.get(),
            "equipment_make": self.make_entry.get(),
            "capacity_t": capacity,
            "conducted_by": {
                "name": self.conducted_name_entry.get(),
                "designation": self.conducted_designation_entry.get()
            },
            "approved_by": {
                "name": self.approved_name_entry.get(),
                "designation": self.approved_designation_entry.get()
            }
        }
        self.save_config()
        messagebox.showinfo("Saved", "Values saved successfully!")

    def start_reading(self):
        try:
            port = self.com_port_entry.get()
            baud = int(self.baud_rate_entry.get())
            self.serial_port = serial.Serial(port, baud, timeout=1)
            self.reading = True
            threading.Thread(target=self.read_data, daemon=True).start()
        except serial.SerialException as e:
            messagebox.showerror("Error", f"Could not open serial port: {e}")

    def read_data(self):
        while self.reading:
            try:
                if self.serial_port.in_waiting:
                    line = self.serial_port.readline().decode().strip()
                    self.root.after(0, self.update_readings, line)
            except Exception as e:
                self.root.after(0, self.result_label.config, {"text": f"Error: {e}", "bg": "red"})
                break

    def update_readings(self, line):
        self.test_load_entry.delete(0, tk.END)
        self.test_load_entry.insert(0, line)
        self.load_cell_value.delete(0, tk.END)
        self.load_cell_value.insert(0, line)
        try:
            load_value = float(line)
            capacity = float(self.capacity_entry.get())
            if load_value <= capacity:
                self.result_label.config(text="RESULT: SUCCESS", bg="lightgreen")
            else:
                self.result_label.config(text="RESULT: FAIL", bg="red")
        except ValueError:
            self.result_label.config(text="RESULT: Invalid Load Value", bg="yellow")

    def stop_reading(self):
        self.reading = False
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()

    def update_data(self, key, value):
        if key == "capacity_t":
            try:
                self.data[key] = float(value)
            except ValueError:
                self.data[key] = value  # Keep as string if not valid float yet
        else:
            self.data[key] = value

    def set_date_to_today(self, event):
        today = datetime.today().strftime('%Y-%m-%d')
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, today)
        self.update_data("date", today)

    def save_to_pdf(self):
        filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(os.getcwd(), filename)
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4

        y = height - 50
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, "Weight Measurement Test Report")
        y -= 40

        c.setFont("Helvetica", 12)
        c.drawString(50, y, f"Date: {self.date_entry.get()}")
        y -= 25
        c.drawString(50, y, f"Equipment Name: {self.name_entry.get()}")
        y -= 25
        c.drawString(50, y, f"Equipment Make: {self.make_entry.get()}")
        y -= 25
        c.drawString(50, y, f"Capacity (T): {self.capacity_entry.get()}")
        y -= 40

        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Conducted By")
        c.setFont("Helvetica", 12)
        y -= 25
        c.drawString(70, y, f"Name: {self.conducted_name_entry.get()}")
        y -= 20
        c.drawString(70, y, f"Designation: {self.conducted_designation_entry.get()}")
        y -= 30

        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Approved By")
        c.setFont("Helvetica", 12)
        y -= 25
        c.drawString(70, y, f"Name: {self.approved_name_entry.get()}")
        y -= 20
        c.drawString(70, y, f"Designation: {self.approved_designation_entry.get()}")
        y -= 40

        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y, "Test Result")
        c.setFont("Helvetica", 12)
        y -= 25
        c.drawString(50, y, f"Test Load (T): {self.test_load_entry.get()}")
        y -= 20
        c.drawString(50, y, f"Load Cell Value: {self.load_cell_value.get()}")
        y -= 20
        c.drawString(50, y, f"Duration (s): {self.duration_entry.get()}")
        y -= 20
        c.drawString(50, y, f"Result: {self.result_label.cget('text')}")
        y -= 40

        c.save()
        messagebox.showinfo("PDF Saved", f"PDF saved as {filename} in {os.getcwd()}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WeightMeasurementApp(root)
    root.mainloop()
