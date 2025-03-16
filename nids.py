import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox, font
import subprocess
import threading
import queue
import os

# GUI for Advanced NIDS
class NIDSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Advanced Network Intrusion Detection System")
        self.root.geometry("900x600")
        self.root.configure(bg="#1E1E1E")  # Dark Theme

        self.nids_path = tk.StringVar()
        self.config_path = tk.StringVar()
        self.log_queue = queue.Queue()

        # Title Label
        title_font = font.Font(family="Arial", size=16, weight="bold")
        title_label = tk.Label(root, text="🔍 Network Intrusion Detection System", font=title_font, fg="white", bg="#1E1E1E")
        title_label.pack(pady=10)

        # Select NIDS Executable
        tk.Button(root, text="📂 Select Snort/Suricata", command=self.select_nids, bg="#3949AB", fg="white", font=("Arial", 10)).pack(pady=5)
        self.nids_label = tk.Label(root, text="No NIDS Selected", fg="yellow", bg="#1E1E1E", font=("Arial", 10))
        self.nids_label.pack()

        # Select Config File
        tk.Button(root, text="📂 Select Config File", command=self.select_config, bg="#3949AB", fg="white", font=("Arial", 10)).pack(pady=5)
        self.config_label = tk.Label(root, text="No Config Selected", fg="yellow", bg="#1E1E1E", font=("Arial", 10))
        self.config_label.pack()

        # Start/Stop Buttons
        tk.Button(root, text="▶ Start Monitoring", command=self.start_monitoring, bg="green", fg="white", font=("Arial", 12, "bold")).pack(pady=5)
        tk.Button(root, text="⏹ Stop Monitoring", command=self.stop_monitoring, bg="red", fg="white", font=("Arial", 12, "bold")).pack(pady=5)

        # Output Log Box
        self.output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=100, height=20, bg="black", fg="lightgreen", font=("Consolas", 10))
        self.output_text.pack(padx=10, pady=10)

        # Thread control
        self.process = None
        self.monitoring = False

        # Schedule log updates
        self.root.after(100, self.update_log)

    def select_nids(self):
        file_path = filedialog.askopenfilename(filetypes=[("Executable Files", "*.exe")])
        if file_path:
            self.nids_path.set(file_path)
            self.nids_label.config(text=f"✅ Selected: {os.path.basename(file_path)}", fg="lightgreen")

    def select_config(self):
        file_path = filedialog.askopenfilename(filetypes=[("Config Files", "*.conf")])
        if file_path:
            self.config_path.set(file_path)
            self.config_label.config(text=f"✅ Selected: {os.path.basename(file_path)}", fg="lightgreen")

    def start_monitoring(self):
        if not self.nids_path.get() or not self.config_path.get():
            messagebox.showerror("Error", "Please select both Snort/Suricata and a config file.")
            return

        self.output_text.insert(tk.END, "\n🚀 Starting Network Monitoring...\n", "info")
        self.output_text.yview(tk.END)
        self.monitoring = True

        threading.Thread(target=self.run_nids, daemon=True).start()

    def stop_monitoring(self):
        if self.process:
            self.process.terminate()
            self.monitoring = False
            self.output_text.insert(tk.END, "\n🚨 Monitoring Stopped.\n", "error")
            self.output_text.yview(tk.END)

    def run_nids(self):
        try:
            self.process = subprocess.Popen(
                [self.nids_path.get(), "-q", "-A", "fast", "-c", self.config_path.get()],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            for line in iter(self.process.stdout.readline, ''):
                if not self.monitoring:
                    break
                self.log_queue.put(line)

        except FileNotFoundError:
            messagebox.showerror("Error", "Snort/Suricata not found. Please select the correct file.")

    def update_log(self):
        while not self.log_queue.empty():
            line = self.log_queue.get_nowait()
            self.output_text.insert(tk.END, line, "alert")
            self.output_text.yview(tk.END)
        self.root.after(100, self.update_log)  # Keep updating log

# Run Application
root = tk.Tk()
app = NIDSApp(root)
root.mainloop()
