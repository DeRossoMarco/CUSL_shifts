import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from .shift_utils import load_availability

class ParametersDialog:
    def __init__(self, config):
        self.dialog = tk.Tk()
        self.dialog.title("Impostazioni Turni")
        self.dialog.cancelled = True
        self.config = config

        # Center the window
        self.center_window()

        self.style = ttk.Style()
        self.style.configure(
            "Custom.TButton",
            font=('Helvetica', 10, 'bold'),
            padding=(10, 5),
            background="#4a90e2",
            foreground="white",
            borderwidth=2,
            relief="raised"
        )
        self.style.map(
            "Custom.TButton",
            background=[("active", "#357ABD"), ("disabled", "#A9A9A9")],
            foreground=[("active", "white"), ("disabled", "#D3D3D3")]
        )

    def center_window(self):
        window_width = 500
        window_height = 300
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.dialog.minsize(500, 300)  # Set minimum window size

    def show(self):
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(sticky='nsew')
        self.dialog.grid_rowconfigure(0, weight=1)
        self.dialog.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        
        # Title section
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 20))
        title_frame.grid_columnconfigure(0, weight=1)
        
        title_label = ttk.Label(title_frame, 
                               text="Configurazione Parametri Turni",
                               font=('Helvetica', 14, 'bold'))
        title_label.grid(row=0, column=0)
        
        # Settings section
        settings_frame = ttk.LabelFrame(main_frame, padding="10")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky='nsew', pady=(0, 20))
        settings_frame.grid_columnconfigure(1, weight=1)
        
        # Min people setting
        ttk.Label(settings_frame, text="Numero minimo:").grid(row=0, column=0, sticky='w', pady=(0, 10))
        min_var = tk.IntVar(value=self.config.MIN_PEOPLE_PER_SHIFT)
        min_frame = ttk.Frame(settings_frame)
        min_frame.grid(row=0, column=1, sticky='ew')
        min_frame.grid_columnconfigure(0, weight=1)
        
        min_entry = ttk.Spinbox(min_frame, from_=1, to=10, textvariable=min_var, width=5)
        min_entry.grid(row=0, column=0, sticky='w')
        
        # Max people setting
        ttk.Label(settings_frame, text="Numero massimo:").grid(row=1, column=0, sticky='w', pady=(0, 10))
        max_var = tk.IntVar(value=self.config.MAX_PEOPLE_PER_SHIFT)
        max_frame = ttk.Frame(settings_frame)
        max_frame.grid(row=1, column=1, sticky='ew')
        max_frame.grid_columnconfigure(0, weight=1)
        
        max_entry = ttk.Spinbox(max_frame, from_=1, to=10, textvariable=max_var, width=5)
        max_entry.grid(row=0, column=0, sticky='w')
        
        # CSV file selection
        csv_path_var = tk.StringVar(value=self.config.CSV_FILE_PATH)
        ttk.Label(settings_frame, text="File CSV:").grid(row=2, column=0, sticky='w', pady=(0, 10))
        csv_frame = ttk.Frame(settings_frame)
        csv_frame.grid(row=2, column=1, sticky='ew')
        csv_frame.grid_columnconfigure(0, weight=1)
        
        csv_entry = ttk.Entry(csv_frame, textvariable=csv_path_var, state='readonly')
        csv_entry.grid(row=0, column=0, sticky='ew')
        
        def select_csv():
            selected = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
            if selected:
                csv_path_var.set(selected)
                self.config.CSV_FILE_PATH = selected

        ttk.Button(
            csv_frame, text="Carica CSV", command=select_csv, style="Custom.TButton"
        ).grid(row=0, column=1, padx=(5, 0))

        def open_availability_only():
            if not self.validate_parameters(min_var, max_var):
                return
            if not self.validate_csv():
                return
            self.update_config(min_var, max_var, csv_path_var)
            self.dialog.cancelled = False  # Not cancelled, but will open GUI directly
            self.dialog.availability_only = True  # Flag to indicate direct GUI opening
            self.dialog.destroy()

        def generate_shifts():
            if not self.validate_parameters(min_var, max_var):
                return
            if not self.validate_csv():
                return
            self.update_config(min_var, max_var, csv_path_var)
            self.dialog.cancelled = False
            self.dialog.availability_only = False  # Normal shift generation
            self.dialog.destroy()

        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Style for accent buttons
        style = ttk.Style()
        style.configure('Accent.TButton', font=('Helvetica', 10, 'bold'))
        
        ttk.Button(
            btn_frame,
            text="Apri Disponibilità",
            command=open_availability_only,
            style='Custom.TButton'
        ).grid(row=0, column=0, padx=5)

        ttk.Button(
            btn_frame,
            text="Genera Turni",
            command=generate_shifts,
            style='Custom.TButton'
        ).grid(row=0, column=1, padx=5)

        self.dialog.protocol("WM_DELETE_WINDOW", self.dialog.destroy)
        self.dialog.mainloop()
        
        # Return tuple of (not cancelled, availability_only)
        return (not self.dialog.cancelled, 
                getattr(self.dialog, 'availability_only', False))

    def select_csv(self, var):
        selected = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if selected:
            var.set(selected)

    def validate_parameters(self, min_var, max_var):
        if min_var.get() > max_var.get():
            messagebox.showerror("Errore", "Il numero minimo non può superare il massimo!")
            return False
        if min_var.get() < 1:
            messagebox.showerror("Errore", "Il numero minimo deve essere almeno 1!")
            return False
        return True

    def update_config(self, min_var, max_var, csv_path_var):
        self.config.MIN_PEOPLE_PER_SHIFT = min_var.get()
        self.config.MAX_PEOPLE_PER_SHIFT = max_var.get()
        self.config.CSV_FILE_PATH = csv_path_var.get()

    def validate_csv(self):
        try:
            availability = load_availability(self.config, self.config.CSV_FILE_PATH)
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nel leggere il CSV:\n{e}")
            return False
        for shift in self.config.weekly_shifts:
            count = sum(1 for person in availability if shift in availability[person])
            if count < self.config.MIN_PEOPLE_PER_SHIFT:
                messagebox.showerror(
                    "Errore",
                    f"Non ci sono abbastanza persone per il turno: {shift}"
                )
                return False
        return True