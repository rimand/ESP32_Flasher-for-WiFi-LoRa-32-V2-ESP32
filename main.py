import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import serial.tools.list_ports
import os
import sys
import json

class ESP32Flasher:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP32 Flasher Tool")
        self.root.geometry("800x750")
        self.root.resizable(True, True)
        self.root.minsize(750, 700)
        
        # Get current directory (where script is located)
        if getattr(sys, 'frozen', False):
            self.current_dir = os.path.dirname(sys.executable)
        else:
            self.current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Set window icon
        self.set_window_icon()
        
        # Config file path
        self.config_file = os.path.join(self.current_dir, "config.json")
        
        # File paths
        self.bootloader_path = ""
        self.partitions_path = ""
        self.boot_app0_file_path = ""
        self.app_bin_path = ""
        self.selected_port = ""
        self.port_trace_id = None
        
        # Find esptool automatically
        self.esptool_path = self.find_esptool()
        
        # Load saved config
        self.load_config()
        
        self.setup_ui()
        self.refresh_ports()
        
        # Update UI with loaded config
        self.update_ui_from_config()
    
    def set_window_icon(self):
        """Set the window icon"""
        try:
            icon_path = os.path.join(self.current_dir, "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
            else:
                # Try to find icon in the same directory as the script
                script_dir = os.path.dirname(os.path.abspath(__file__)) if not getattr(sys, 'frozen', False) else self.current_dir
                icon_path = os.path.join(script_dir, "icon.ico")
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
        except Exception as e:
            # If icon can't be set, just continue without it
            print(f"Could not set icon: {e}")
        
    def setup_ui(self):
        # Configure root grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)  # Status text area should expand
        
        # Title
        title_label = ttk.Label(main_frame, text="ESP32 Flasher", font=("Arial", 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        # COM Port Selection
        port_frame = ttk.LabelFrame(main_frame, text="COM Port Selection", padding="12")
        port_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        port_frame.columnconfigure(1, weight=1)
        
        ttk.Label(port_frame, text="Port:", font=("Arial", 10)).grid(row=0, column=0, padx=(5, 10), pady=8, sticky=tk.W)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(port_frame, textvariable=self.port_var, width=20, state="readonly", font=("Arial", 9))
        self.port_combo.grid(row=0, column=1, padx=5, pady=8, sticky=(tk.W, tk.E))
        
        refresh_btn = ttk.Button(port_frame, text="Refresh", command=self.refresh_ports, width=12)
        refresh_btn.grid(row=0, column=2, padx=(5, 5), pady=8)
        
        # ESPTool Path Selection
        esptool_frame = ttk.LabelFrame(main_frame, text="ESP Tool Path", padding="12")
        esptool_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        esptool_frame.columnconfigure(1, weight=1)
        
        ttk.Label(esptool_frame, text="esptool.exe:", font=("Arial", 10)).grid(row=0, column=0, padx=(5, 10), pady=8, sticky=tk.W)
        self.esptool_label = ttk.Label(esptool_frame, text="Not found", foreground="red", font=("Arial", 9), wraplength=450)
        self.esptool_label.grid(row=0, column=1, padx=5, pady=8, sticky=(tk.W, tk.E))
        ttk.Button(esptool_frame, text="Browse", command=self.select_esptool, width=12).grid(row=0, column=2, padx=(5, 5), pady=8)
        
        if self.esptool_path:
            self.esptool_label.config(text=os.path.basename(self.esptool_path), foreground="green")
        
        # File Selection Frame
        file_frame = ttk.LabelFrame(main_frame, text="Binary Files", padding="12")
        file_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        file_frame.columnconfigure(1, weight=1)
        
        # Bootloader (0x1000)
        ttk.Label(file_frame, text="Bootloader.bin (0x1000):", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.W, padx=(5, 10), pady=6)
        self.bootloader_label = ttk.Label(file_frame, text="Not selected", foreground="gray", font=("Arial", 9))
        self.bootloader_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=6)
        ttk.Button(file_frame, text="Browse", command=self.select_bootloader, width=12).grid(row=0, column=2, padx=(5, 5), pady=6)
        
        # Partitions (0x8000)
        ttk.Label(file_frame, text="Partitions.bin (0x8000):", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.W, padx=(5, 10), pady=6)
        self.partitions_label = ttk.Label(file_frame, text="Not selected", foreground="gray", font=("Arial", 9))
        self.partitions_label.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=6)
        ttk.Button(file_frame, text="Browse", command=self.select_partitions, width=12).grid(row=1, column=2, padx=(5, 5), pady=6)
        
        # Boot App0 (0xe000)
        ttk.Label(file_frame, text="boot_app0.bin (0xe000):", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.W, padx=(5, 10), pady=6)
        self.boot_app0_label = ttk.Label(file_frame, text="Not selected", foreground="gray", font=("Arial", 9))
        self.boot_app0_label.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=6)
        ttk.Button(file_frame, text="Browse", command=self.select_boot_app0, width=12).grid(row=2, column=2, padx=(5, 5), pady=6)
        
        # Application Binary (0x10000)
        ttk.Label(file_frame, text="LoRaController.ino.bin (0x10000):", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.W, padx=(5, 10), pady=6)
        self.app_bin_label = ttk.Label(file_frame, text="Not selected", foreground="gray", font=("Arial", 9))
        self.app_bin_label.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=5, pady=6)
        ttk.Button(file_frame, text="Browse", command=self.select_app_bin, width=12).grid(row=3, column=2, padx=(5, 5), pady=6)
        
        # Flash Button
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(10, 10))
        flash_btn = ttk.Button(button_frame, text="Flash ESP32", command=self.flash_esp32, width=20)
        flash_btn.pack()
        
        # Progress/Status Frame
        status_frame = ttk.LabelFrame(main_frame, text="Status Log", padding="10")
        status_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        # Status text with scrollbar
        text_scroll_frame = ttk.Frame(status_frame)
        text_scroll_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_scroll_frame.columnconfigure(0, weight=1)
        text_scroll_frame.rowconfigure(0, weight=1)
        
        self.status_text = tk.Text(text_scroll_frame, height=12, wrap=tk.WORD, state=tk.DISABLED, 
                                   font=("Consolas", 9), bg="#f5f5f5", relief=tk.SUNKEN, bd=1)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(text_scroll_frame, orient="vertical", command=self.status_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=scrollbar.set)
    
    def save_config(self):
        """Save current configuration to JSON file"""
        config = {
            "port": self.port_var.get() if hasattr(self, 'port_var') else self.selected_port,
            "esptool_path": self.esptool_path or "",
            "bootloader_path": self.bootloader_path or "",
            "partitions_path": self.partitions_path or "",
            "boot_app0_path": self.boot_app0_file_path or "",
            "app_bin_path": self.app_bin_path or ""
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            if hasattr(self, 'status_text'):
                self.log_status(f"Warning: Could not save config: {e}")
            else:
                print(f"Warning: Could not save config: {e}")
    
    def load_config(self):
        """Load configuration from JSON file"""
        if not os.path.exists(self.config_file):
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Load values
            self.selected_port = config.get("port", "")
            if config.get("esptool_path") and os.path.exists(config.get("esptool_path")):
                self.esptool_path = config.get("esptool_path")
            if config.get("bootloader_path") and os.path.exists(config.get("bootloader_path")):
                self.bootloader_path = config.get("bootloader_path")
            if config.get("partitions_path") and os.path.exists(config.get("partitions_path")):
                self.partitions_path = config.get("partitions_path")
            if config.get("boot_app0_path") and os.path.exists(config.get("boot_app0_path")):
                self.boot_app0_file_path = config.get("boot_app0_path")
            if config.get("app_bin_path") and os.path.exists(config.get("app_bin_path")):
                self.app_bin_path = config.get("app_bin_path")
                
        except Exception as e:
            # Can't use log_status here as UI might not be ready yet
            print(f"Warning: Could not load config: {e}")
    
    def update_ui_from_config(self):
        """Update UI elements with loaded config"""
        # Update port
        if hasattr(self, 'port_combo') and self.selected_port:
            ports = list(self.port_combo['values'])
            if self.selected_port in ports:
                self.port_var.set(self.selected_port)
                self.port_combo.current(ports.index(self.selected_port))
        
        # Update esptool label
        if hasattr(self, 'esptool_label'):
            if self.esptool_path:
                if self.esptool_path == "esptool.py":
                    self.esptool_label.config(text="esptool.py (from PATH)", foreground="green")
                else:
                    self.esptool_label.config(text=os.path.basename(self.esptool_path), foreground="green")
            else:
                self.esptool_label.config(text="Not found", foreground="red")
        
        # Update file labels
        if hasattr(self, 'bootloader_label') and self.bootloader_path:
            self.bootloader_label.config(text=os.path.basename(self.bootloader_path), foreground="green")
        
        if hasattr(self, 'partitions_label') and self.partitions_path:
            self.partitions_label.config(text=os.path.basename(self.partitions_path), foreground="green")
        
        if hasattr(self, 'boot_app0_label') and self.boot_app0_file_path:
            self.boot_app0_label.config(text=os.path.basename(self.boot_app0_file_path), foreground="green")
        
        if hasattr(self, 'app_bin_label') and self.app_bin_path:
            self.app_bin_label.config(text=os.path.basename(self.app_bin_path), foreground="green")
        
        if any([self.bootloader_path, self.partitions_path, self.boot_app0_file_path, self.app_bin_path]):
            self.log_status("Configuration loaded from config.json")
        
    def find_esptool(self):
        """Try to find esptool.exe automatically"""
        possible_paths = []
        
        # Get username from environment
        username = os.getenv('USERNAME') or os.getenv('USER')
        
        # Common Arduino paths
        if username:
            arduino_paths = [
                os.path.join(os.path.expanduser("~"), "Documents", "Arduino", "hardware", "heltec", "esp32", "tools", "esptool", "esptool.exe"),
                os.path.join(os.path.expanduser("~"), "Documents", "Arduino", "hardware", "espressif", "esp32", "tools", "esptool", "esptool.exe"),
                os.path.join("C:", "Users", username, "Documents", "Arduino", "hardware", "heltec", "esp32", "tools", "esptool", "esptool.exe"),
                os.path.join("C:", "Users", username, "Documents", "Arduino", "hardware", "espressif", "esp32", "tools", "esptool", "esptool.exe"),
            ]
            possible_paths.extend(arduino_paths)
        
        # Search in common Arduino installation locations
        for drive in ["C:", "D:"]:
            if os.path.exists(drive):
                # Search for Arduino folders
                arduino_base = os.path.join(drive, "Users")
                if os.path.exists(arduino_base):
                    for user_folder in os.listdir(arduino_base):
                        user_path = os.path.join(arduino_base, user_folder)
                        if os.path.isdir(user_path):
                            arduino_docs = os.path.join(user_path, "Documents", "Arduino", "hardware")
                            if os.path.exists(arduino_docs):
                                # Search for heltec or espressif
                                for vendor in ["heltec", "espressif"]:
                                    vendor_path = os.path.join(arduino_docs, vendor, "esp32", "tools", "esptool", "esptool.exe")
                                    if os.path.exists(vendor_path):
                                        possible_paths.append(vendor_path)
        
        # Check if esptool is in PATH (installed via pip)
        try:
            result = subprocess.run(["esptool.py", "--version"], 
                                  capture_output=True, 
                                  timeout=2)
            if result.returncode == 0:
                return "esptool.py"  # Use esptool.py from PATH
        except:
            pass
        
        # Check all possible paths
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def select_esptool(self):
        """Let user select esptool.exe manually"""
        filename = filedialog.askopenfilename(
            title="Select esptool.exe",
            initialdir=os.path.dirname(self.esptool_path) if self.esptool_path else self.current_dir,
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename and os.path.exists(filename):
            self.esptool_path = filename
            self.esptool_label.config(text=os.path.basename(filename), foreground="green")
            self.log_status(f"Selected esptool: {filename}")
            self.save_config()
        elif filename:
            messagebox.showerror("Error", "Selected file does not exist!")
    
    def refresh_ports(self):
        """Refresh available COM ports"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            # Try to restore saved port, otherwise select first
            if self.selected_port and self.selected_port in ports:
                self.port_var.set(self.selected_port)
                self.port_combo.current(ports.index(self.selected_port))
            else:
                self.port_combo.current(0)
                self.selected_port = ports[0] if ports else ""
                if self.selected_port:
                    self.save_config()
        
        # Save port selection when changed (only set trace once)
        if self.port_trace_id is None and hasattr(self, 'port_var'):
            self.port_trace_id = self.port_var.trace_add('write', lambda *args: self.on_port_changed())
        
        self.log_status(f"Found {len(ports)} COM port(s)")
    
    def on_port_changed(self):
        """Called when port selection changes"""
        self.selected_port = self.port_var.get()
        self.save_config()
        
    def log_status(self, message):
        """Add message to status text"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update()
        
    def select_bootloader(self):
        """Select bootloader.bin file"""
        initialdir = os.path.dirname(self.bootloader_path) if self.bootloader_path else self.current_dir
        filename = filedialog.askopenfilename(
            title="Select Bootloader.bin",
            initialdir=initialdir,
            filetypes=[("Binary files", "*.bin"), ("All files", "*.*")]
        )
        if filename:
            self.bootloader_path = filename
            self.bootloader_label.config(text=os.path.basename(filename), foreground="green")
            self.log_status(f"Selected bootloader: {filename}")
            self.save_config()
            
    def select_partitions(self):
        """Select partitions.bin file"""
        initialdir = os.path.dirname(self.partitions_path) if self.partitions_path else self.current_dir
        filename = filedialog.askopenfilename(
            title="Select Partitions.bin",
            initialdir=initialdir,
            filetypes=[("Binary files", "*.bin"), ("All files", "*.*")]
        )
        if filename:
            self.partitions_path = filename
            self.partitions_label.config(text=os.path.basename(filename), foreground="green")
            self.log_status(f"Selected partitions: {filename}")
            self.save_config()
            
    def select_boot_app0(self):
        """Select boot_app0.bin file"""
        initialdir = os.path.dirname(self.boot_app0_file_path) if self.boot_app0_file_path else self.current_dir
        filename = filedialog.askopenfilename(
            title="Select boot_app0.bin",
            initialdir=initialdir,
            filetypes=[("Binary files", "*.bin"), ("All files", "*.*")]
        )
        if filename:
            self.boot_app0_file_path = filename
            self.boot_app0_label.config(text=os.path.basename(filename), foreground="green")
            self.log_status(f"Selected boot_app0: {filename}")
            self.save_config()
            
    def select_app_bin(self):
        """Select application binary file"""
        initialdir = os.path.dirname(self.app_bin_path) if self.app_bin_path else self.current_dir
        filename = filedialog.askopenfilename(
            title="Select LoRaController.ino.bin",
            initialdir=initialdir,
            filetypes=[("Binary files", "*.bin"), ("All files", "*.*")]
        )
        if filename:
            self.app_bin_path = filename
            self.app_bin_label.config(text=os.path.basename(filename), foreground="green")
            self.log_status(f"Selected application binary: {filename}")
            self.save_config()
            
    def validate_inputs(self):
        """Validate all inputs before flashing"""
        if not self.port_var.get():
            messagebox.showerror("Error", "Please select a COM port")
            return False
            
        if not self.bootloader_path:
            messagebox.showerror("Error", "Please select bootloader.bin file")
            return False
            
        if not self.partitions_path:
            messagebox.showerror("Error", "Please select partitions.bin file")
            return False
            
        if not self.boot_app0_file_path:
            messagebox.showerror("Error", "Please select boot_app0.bin file")
            return False
            
        if not self.app_bin_path:
            messagebox.showerror("Error", "Please select LoRaController.ino.bin file")
            return False
            
        if not self.esptool_path:
            messagebox.showerror("Error", "Please select esptool.exe path")
            return False
        
        # Check if esptool.py (from pip) or esptool.exe exists
        if self.esptool_path == "esptool.py":
            # Check if esptool.py is available in PATH
            try:
                result = subprocess.run(["esptool.py", "--version"], 
                                      capture_output=True, 
                                      timeout=2)
                if result.returncode != 0:
                    messagebox.showerror("Error", "esptool.py not found in PATH. Please install it with: pip install esptool")
                    return False
            except:
                messagebox.showerror("Error", "esptool.py not found in PATH. Please install it with: pip install esptool")
                return False
        elif not os.path.exists(self.esptool_path):
            messagebox.showerror("Error", f"esptool.exe not found at:\n{self.esptool_path}\n\nPlease select the correct path.")
            return False
            
        return True
        
    def flash_esp32(self):
        """Execute the flash command"""
        if not self.validate_inputs():
            return
            
        port = self.port_var.get()
        
        # Build the esptool command
        cmd = [
            self.esptool_path,
            "--chip", "esp32",
            "--port", port,
            "--baud", "921600",
            "--before", "default_reset",
            "--after", "hard_reset",
            "write_flash",
            "-z",
            "--flash_mode", "keep",
            "--flash_freq", "keep",
            "--flash_size", "keep",
            "0x1000", self.bootloader_path,
            "0x8000", self.partitions_path,
            "0xe000", self.boot_app0_file_path,
            "0x10000", self.app_bin_path
        ]
        
        self.log_status("=" * 60)
        self.log_status("Starting flash process...")
        self.log_status(f"Port: {port}")
        self.log_status(f"Bootloader: {os.path.basename(self.bootloader_path)}")
        self.log_status(f"Partitions: {os.path.basename(self.partitions_path)}")
        self.log_status(f"Boot App0: {os.path.basename(self.boot_app0_file_path)}")
        self.log_status(f"Application: {os.path.basename(self.app_bin_path)}")
        self.log_status("=" * 60)
        
        try:
            # Execute the command
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Read output in real-time
            for line in process.stdout:
                self.log_status(line.strip())
                
            process.wait()
            
            if process.returncode == 0:
                self.log_status("=" * 60)
                self.log_status("Flash completed successfully!")
                messagebox.showinfo("Success", "ESP32 flashed successfully!")
            else:
                self.log_status("=" * 60)
                self.log_status(f"Flash failed with return code: {process.returncode}")
                messagebox.showerror("Error", "Flash process failed. Check the output above.")
                
        except Exception as e:
            self.log_status(f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ESP32Flasher(root)
    root.mainloop()

