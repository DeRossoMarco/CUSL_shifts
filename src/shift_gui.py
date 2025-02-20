import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import platform
import os
from PIL import Image, ImageDraw, ImageFont
from .loading_screen import LoadingScreen

class ShiftGUI:
    def __init__(self, config, shifts, weekly_shifts, availability, reload_func, calculate_shifts):
        self.config = config
        self.shifts = shifts
        self.weekly_shifts = weekly_shifts
        self.availability = availability
        self.reload_func = reload_func
        self.calculate_shifts = calculate_shifts
        self.root = tk.Tk()
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

    def show(self):
        self.root.title("Turni Settimanali")
        self.root.minsize(800, 600)
        
        # Configure window size and position
        window_width = 1000
        window_height = 800
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Configure main window grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Main container frame
        container = ttk.Frame(self.root)
        container.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        
        # Configure container grid
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=4)
        container.grid_columnconfigure(1, weight=1)
        
        # Schedule frame (left side)
        frame = ttk.Frame(container)
        frame.grid(row=0, column=0, sticky='nsew', padx=(0, 5))
        
        # Right panel frame
        right_frame = ttk.Frame(container)
        right_frame.grid(row=0, column=1, sticky='nsew', padx=(5, 0))
        
        # Configure right frame grid
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
        
        # Style configuration
        style = ttk.Style()
        style.configure("Header.TLabel", background="#4a90e2", foreground="white", font=('Helvetica', 10, 'bold'))
        style.configure("Unassigned.TLabel", background="#f0f0f0", font=('Helvetica', 10, 'bold'))
        
        # Unassigned section header
        unassigned_label = ttk.Label(
            right_frame, text="Mancanti", style="Unassigned.TLabel"
        )
        unassigned_label.grid(row=0, column=0, sticky='ew', pady=(0, 5))
        
        # Unassigned list
        unassigned_list = tk.Listbox(
            right_frame, font=('Helvetica', 9),
            selectmode='none', relief='solid', bd=1
        )
        unassigned_list.grid(row=1, column=0, sticky='nsew')

        days = ['lunedi', 'martedi', 'mercoledi', 'giovedi', 'venerdi']
        slots = ['m', 'pr', 'po']
        slot_labels = {'m': 'Mattina', 'pr': 'Pranzo', 'po': 'Pomeriggio'}

        total_rows = len(slots) * 2 + 2
        total_cols = len(days) * 2 + 1
        
        for i in range(total_rows):
            frame.grid_rowconfigure(i, weight=1, minsize=15)
        for j in range(total_cols):
            frame.grid_columnconfigure(j, weight=1, minsize=15)

        for j, day in enumerate(days):
            header = tk.Label(frame, text=day.capitalize(),
                             fg="white", 
                             font=('Helvetica', 8, 'bold'),
                             pady=3,
                             padx=1)
            header.grid(row=0, column=j*2 + 1, sticky='nsew')
        
        for i, slot in enumerate(slots):
            header = tk.Label(frame, text=slot_labels[slot],
                             fg="white",
                             font=('Helvetica', 8, 'bold'),
                             padx=2)
            header.grid(row=i*2 + 1, column=0, sticky='nsew')

        checkboxes = {}
        cell_frames = {}
        indicators = {}

        def create_indicator(parent):
            canvas = tk.Canvas(parent, width=120, height=12, highlightthickness=0)
            rectangle = canvas.create_rectangle(0, 0, 120, 12, fill='#ffff33')
            return canvas, rectangle

        def validate_slot(slot):
            checked_count = sum(
                1 for (p, s), var in checkboxes.items()
                if s == slot and var.get() is True
            )
            if checked_count < self.config.MIN_PEOPLE_PER_SHIFT:
                return '#ffff33'
            elif checked_count > self.config.MAX_PEOPLE_PER_SHIFT:
                return '#ff0000'
            else:
                return '#66ff66'

        def update_slot_color(slot):
            color = validate_slot(slot)
            canvas, circle = indicators[slot]
            canvas.itemconfig(circle, fill=color)

        def get_unassigned_people():
            assigned = set()
            for (persona, slot), var in checkboxes.items():
                if var.get():
                    assigned.add(persona)
            return sorted(set(self.availability.keys()) - assigned)

        def update_unassigned_list():
            unassigned_list.delete(0, tk.END)
            unassigned = get_unassigned_people()
            for person in unassigned:
                unassigned_list.insert(tk.END, person)
            if unassigned:
                unassigned_list.configure(bg='#ff0000')
            else:
                unassigned_list.configure(bg='#66ff66')

        def on_checkbox_change(persona, current_slot):
            if checkboxes[(persona, current_slot)].get():
                for slot in self.weekly_shifts:
                    if slot != current_slot and (persona, slot) in checkboxes:
                        checkboxes[(persona, slot)].set(False)
                        update_slot_color(slot)
            update_slot_color(current_slot)
            update_unassigned_list()

        for i, slot in enumerate(slots):
            for j, day in enumerate(days):
                day_slot = f"{day}_{slot}"
                assigned_people = [
                    p for g, t in self.shifts if g == day_slot for p in t
                ]
                available_people = [
                    p for p, ds in self.availability.items() if day_slot in ds
                ]
                all_people = sorted(set(assigned_people) | set(available_people))

                cell_frame = tk.Frame(frame, relief="solid", borderwidth=1)
                cell_frame.grid(
                    row=i*2 + 1, column=j*2 + 1, sticky='nsew',
                    padx=1, pady=1, ipadx=1, ipady=1
                )
                cell_frames[day_slot] = cell_frame

                indicator_canvas, indicator_circle = create_indicator(cell_frame)
                indicator_canvas.grid(row=0, column=0, sticky='ew', columnspan=2)
                indicators[day_slot] = (indicator_canvas, indicator_circle)

                checkbox_frame = tk.Frame(cell_frame)
                checkbox_frame.grid(row=1, column=0, sticky='nsew')
                checkbox_frame.grid_columnconfigure(0, weight=1)

                for persona in all_people:
                    var = tk.BooleanVar(value=(persona in assigned_people))
                    check = tk.Checkbutton(
                        checkbox_frame, 
                        text=persona, 
                        variable=var,
                        command=lambda p=persona, s=day_slot: on_checkbox_change(p, s),
                        font=('Helvetica', 8),
                        wraplength=100,
                        justify='left'
                    )
                    check.grid(sticky='ew', padx=0, pady=0)
                    checkboxes[(persona, day_slot)] = var
                
                update_slot_color(day_slot)
                
        def recalculate_shifts():
            self.root.destroy()
            screen = LoadingScreen(on_cancel=self.reload_func)
            screen.window.after(100, self.calculate_shifts, screen)
            screen.mainloop()

        def get_system_font():
            system = platform.system()
            if system == 'Windows':
                return 'arial.ttf'
            elif system == 'Darwin':
                return '/System/Library/Fonts/Helvetica.ttc'
            else:
                font_paths = [
                    '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
                    '/usr/share/fonts/TTF/DejaVuSans.ttf',
                    '/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf'
                ]
                for path in font_paths:
                    if os.path.exists(path):
                        return path
                return None

        def save_image():
            try:
                filetypes = [
                    ('PNG Image', '*.png'),
                    ('JPEG Image', '*.jpg'),
                    ('Bitmap Image', '*.bmp')
                ]
                filename = filedialog.asksaveasfilename(
                    defaultextension=".png",
                    filetypes=filetypes,
                    title="Salva immagine turni",
                    initialfile="turni_settimanali"
                )
                
                if not filename:
                    return

                img_width, img_height = 2600, 1800
                img = Image.new('RGB', (img_width, img_height), 'white')
                draw = ImageDraw.Draw(img)

                system_font = get_system_font()
                try:
                    if (system_font):
                        header_font = ImageFont.truetype(system_font, 40)
                        content_font = ImageFont.truetype(system_font, 60)
                    else:
                        header_font = ImageFont.load_default()
                        content_font = ImageFont.load_default()
                except:
                    header_font = ImageFont.load_default()
                    content_font = ImageFont.load_default()

                margin_top, margin_left = 200, 250
                margin_right, margin_bottom = 150, 150
                usable_width = img_width - margin_left - margin_right
                usable_height = img_height - margin_top - margin_bottom
                cell_width = usable_width // 5
                cell_height = usable_height // 3

                def get_text_dimensions(text, font):
                    bbox = draw.textbbox((0, 0), text, font=font)
                    return bbox[2] - bbox[0], bbox[3] - bbox[1]

                def draw_centered_text(text, x, y, font, fill='black'):
                    text_width, text_height = get_text_dimensions(text, font)
                    text_x = x - text_width // 2
                    text_y = y - text_height // 2
                    draw.text((text_x, text_y), text, font=font, fill=fill)

                days_labels = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì']
                for j, day in enumerate(days_labels):
                    x = margin_left + j * cell_width + cell_width // 2
                    draw_centered_text(day, x, margin_top - 50, header_font)

                slots_labels = ['Mattina', 'Pranzo', 'Pomeriggio']
                for i, slot in enumerate(slots_labels):
                    y = margin_top + i * cell_height + cell_height // 2
                    draw_centered_text(slot, margin_left - 130, y, header_font)

                def wrap_text(text, font, max_width):
                    words = text.split()
                    lines = []
                    current_line = []
                    for word in words:
                        test_line = ' '.join(current_line + [word])
                        text_width, _ = get_text_dimensions(test_line, font)
                        if text_width <= max_width:
                            current_line.append(word)
                        else:
                            lines.append(' '.join(current_line))
                            current_line = [word]
                    if current_line:
                        lines.append(' '.join(current_line))
                    return lines

                for i, time_slot in enumerate(['m', 'pr', 'po']):
                    for j, day_name in enumerate(['lunedi', 'martedi',
                                                  'mercoledi', 'giovedi', 'venerdi']):
                        shift_key = f"{day_name}_{time_slot}"
                        cell_x = margin_left + j * cell_width
                        cell_y = margin_top + i * cell_height
                        selected_people = sorted(
                            [p.capitalize() for (p, s), var in
                             checkboxes.items() if s == shift_key and var.get()]
                        )
                        max_text_width = cell_width - 40
                        _, text_height = get_text_dimensions("Test", content_font)
                        line_height = text_height + 15
                        wrapped_lines = []
                        for person in selected_people:
                            wrapped_lines.extend(wrap_text(person, content_font, max_text_width))
                        total_text_height = len(wrapped_lines) * line_height
                        start_y = cell_y + (cell_height - total_text_height) // 2

                        for line in wrapped_lines:
                            text_width, _ = get_text_dimensions(line, content_font)
                            text_x = cell_x + (cell_width - text_width) // 2
                            draw.text((text_x, start_y), line, font=content_font, fill='black')
                            start_y += line_height

                for i in range(4):
                    y_line = margin_top + i * cell_height
                    draw.line([(margin_left, y_line), (margin_left + 5 * cell_width, y_line)], fill='black', width=2)

                for j in range(6):
                    x_line = margin_left + j * cell_width
                    draw.line([(x_line, margin_top), (x_line, margin_top + 3 * cell_height)], fill='black', width=2)

                img.save(filename)
                messagebox.showinfo("Successo", "Immagine salvata correttamente!")
            except Exception as e:
                messagebox.showerror("Errore", f"Errore nel salvare l'immagine:\n{str(e)}")

        giorni_map = {
            'lunedi': 'lunedi', 'martedi': 'martedi',
            'mercoledi': 'mercoledi', 'giovedi': 'giovedi',
            'venerdi': 'venerdi'
        }
        slots_map = {'m': 'Mattina', 'pr': 'Pranzo', 'po': 'Pomeriggio'}

        button_frame = ttk.Frame(frame)
        button_frame.grid(
            row=len(slots)*2 + 1, column=0,
            columnspan=len(days)*2 + 1, pady=10
        )

        recalc_button = ttk.Button(
            button_frame, text="Ricalcola Turni",
            command=recalculate_shifts, style="Custom.TButton"
        )
        recalc_button.grid(row=0, column=0, padx=5)

        print_button = ttk.Button(
            button_frame, text="Salva Immagine",
            command=save_image, style="Custom.TButton"
        )
        print_button.grid(row=0, column=1, padx=5)

        def go_back_to_parameters():
            self.root.destroy()
            self.reload_func()

        back_button = ttk.Button(
            button_frame, text="Indietro",
            command=go_back_to_parameters, style="Custom.TButton"
        )
        back_button.grid(row=0, column=2, padx=5)

        update_unassigned_list()
        self.root.mainloop()