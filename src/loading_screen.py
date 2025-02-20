import tkinter as tk
from tkinter import ttk

class LoadingScreen:
    def __init__(self, on_cancel):
        self.window = tk.Tk()
        self.window.title("Calcolo Turni")
        self.window.config(cursor="arrow")
        
        # Set minimum window size
        self.window.minsize(300, 200)
        
        # Add cancelled flag and after_id
        self.cancelled = False
        self.after_id = None
        self.arc_start = 0
        self.on_cancel = on_cancel
        
        # Configure window grid
        self.window.grid_rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        
        # Center the window
        window_width = 400
        window_height = 200
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Main frame
        self.frame = ttk.Frame(self.window)
        self.frame.config(cursor="arrow")
        self.frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)
        
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        
        # Add label
        self.label = ttk.Label(self.frame, text="Calcolo dei turni in corso...",
                             font=('Helvetica', 12))
        self.label.grid(row=0, column=0, pady=10)
        
        # Add canvas
        canvas_size = 40
        self.canvas = tk.Canvas(self.frame, width=canvas_size, height=canvas_size,
                              highlightthickness=0)
        self.canvas.grid(row=1, column=0, pady=10)
        
        # Create arc
        self.arc = self.canvas.create_arc(4, 4, canvas_size-4, canvas_size-4,
                                        start=self.arc_start, extent=300,
                                        style=tk.ARC, width=4)
        
        # Add cancel button
        self.cancel_button = ttk.Button(self.frame, text="Annulla",
                                      command=self.cleanup, cursor="arrow")
        self.cancel_button.grid(row=2, column=0, pady=10)
        
        # Set up close handler
        self.window.protocol("WM_DELETE_WINDOW", self.cleanup)
        
        # Start animation
        self.spin_animation()
    
    def spin_animation(self):
        if not self.cancelled and self.window.winfo_exists():
            self.arc_start = (self.arc_start - 10) % 360
            self.canvas.itemconfig(self.arc, start=self.arc_start)
            self.after_id = self.window.after(50, self.spin_animation)
    
    def cleanup(self):
        if self.after_id:
            self.window.after_cancel(self.after_id)
        self.cancelled = True
        self.window.destroy()
        self.on_cancel()
    
    def mainloop(self):
        self.window.mainloop()
    
    def destroy(self):
        if self.after_id:
            self.window.after_cancel(self.after_id)
        self.window.destroy()
    
    def after(self, ms, func):
        return self.window.after(ms, func)
    
    def update(self):
        return self.window.update()
    
    def winfo_exists(self):
        return self.window.winfo_exists()