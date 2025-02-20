import random
import csv
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont
import platform
import os

# definition of week shifts
weekly_shifts = [
    'lunedi_m', 'lunedi_pr', 'lunedi_po',
    'martedi_m', 'martedi_pr', 'martedi_po',
    'mercoledi_m', 'mercoledi_pr', 'mercoledi_po',
    'giovedi_m', 'giovedi_pr', 'giovedi_po',
    'venerdi_m', 'venerdi_pr', 'venerdi_po'
]

# Global parameters for shift size
MIN_PEOPLE_PER_SHIFT = 2
MAX_PEOPLE_PER_SHIFT = 3
CSV_FILE_PATH = "disponibilita.csv"

def show_parameters_dialog():
    dialog = tk.Tk()
    dialog.title("Impostazioni Turni")
        
    # Add cancelled flag
    dialog.cancelled = True  # Default to True, set to False only on successful validation
    
    # Configure window grid
    dialog.grid_rowconfigure(0, weight=1)
    dialog.grid_columnconfigure(0, weight=1)

    # Set minimum window size
    dialog.minsize(400, 300)
    
    # Center the window with initial size
    window_width = 500
    window_height = 200
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Main container with padding
    main_frame = ttk.Frame(dialog, padding="20")
    main_frame.grid(row=0, column=0, sticky='nsew')
    main_frame.grid_columnconfigure(0, weight=1)
    
    # Title section
    title_frame = ttk.Frame(main_frame)
    title_frame.grid(row=0, column=0, sticky='ew', pady=(0, 20))
    title_frame.grid_columnconfigure(0, weight=1)
    
    title_label = ttk.Label(title_frame, 
                           text="Configurazione Parametri Turni",
                           font=('Helvetica', 14, 'bold'))
    title_label.grid(row=0, column=0)
    
    # Settings section
    settings_frame = ttk.LabelFrame(main_frame, padding="10")
    settings_frame.grid(row=1, column=0, sticky='nsew', pady=(0, 20))
    settings_frame.grid_columnconfigure(1, weight=1)
    
    # Min people setting
    ttk.Label(settings_frame, text="Numero minimo:").grid(row=0, column=0, sticky='w', pady=(0, 10))
    min_var = tk.IntVar(value=MIN_PEOPLE_PER_SHIFT)
    min_frame = ttk.Frame(settings_frame)
    min_frame.grid(row=0, column=1, sticky='ew')
    min_frame.grid_columnconfigure(0, weight=1)
    
    min_entry = ttk.Spinbox(min_frame, from_=1, to=10, textvariable=min_var, width=5)
    min_entry.grid(row=0, column=0, sticky='w')
    
    # Max people setting
    ttk.Label(settings_frame, text="Numero massimo:").grid(row=1, column=0, sticky='w', pady=(0, 10))
    max_var = tk.IntVar(value=MAX_PEOPLE_PER_SHIFT)
    max_frame = ttk.Frame(settings_frame)
    max_frame.grid(row=1, column=1, sticky='ew')
    max_frame.grid_columnconfigure(0, weight=1)
    
    max_entry = ttk.Spinbox(max_frame, from_=1, to=10, textvariable=max_var, width=5)
    max_entry.grid(row=0, column=0, sticky='w')
    
    # CSV file selection
    csv_path_var = tk.StringVar(value=CSV_FILE_PATH)
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
            global CSV_FILE_PATH
            CSV_FILE_PATH = selected

    ttk.Button(csv_frame, text="Carica CSV", command=select_csv).grid(row=0, column=1, padx=(5, 0))
    
    def validate_and_close():
        min_val = min_var.get()
        max_val = max_var.get()
        if min_val > max_val:
            messagebox.showerror("Errore", "Il numero minimo non può essere maggiore del massimo!")
            return
        if min_val < 1:
            messagebox.showerror("Errore", "Il numero minimo deve essere almeno 1!")
            return
        global MIN_PEOPLE_PER_SHIFT, MAX_PEOPLE_PER_SHIFT
        MIN_PEOPLE_PER_SHIFT = min_val
        MAX_PEOPLE_PER_SHIFT = max_val
        dialog.cancelled = False  # Set to False only on successful validation
        dialog.destroy()
    
    def open_gui_availability_only():
        min_val = min_var.get()
        max_val = max_var.get()
        if min_val > max_val:
            messagebox.showerror("Errore", "Il numero minimo non può essere maggiore del massimo!")
            return
        if min_val < 1:
            messagebox.showerror("Errore", "Il numero minimo deve essere almeno 1!")
            return
        global MIN_PEOPLE_PER_SHIFT, MAX_PEOPLE_PER_SHIFT
        MIN_PEOPLE_PER_SHIFT = min_val
        MAX_PEOPLE_PER_SHIFT = max_val
        dialog.destroy()
        # Load CSV and open GUI with empty shifts
        availability = load_availability_from_csv(CSV_FILE_PATH, weekly_shifts)
        create_gui([], weekly_shifts, availability)

    def open_gui_with_shifts():
        min_val = min_var.get()
        max_val = max_var.get()
        if min_val > max_val:
            messagebox.showerror("Errore", "Il numero minimo non può essere maggiore del massimo!")
            return
        if min_val < 1:
            messagebox.showerror("Errore", "Il numero minimo deve essere almeno 1!")
            return
        global MIN_PEOPLE_PER_SHIFT, MAX_PEOPLE_PER_SHIFT
        MIN_PEOPLE_PER_SHIFT = min_val
        MAX_PEOPLE_PER_SHIFT = max_val
        dialog.destroy()
        # Same approach as main: load availability, show loading screen, then create GUI
        availability = load_availability_from_csv(CSV_FILE_PATH, weekly_shifts)
        loading_window = show_loading_screen()
        def calculate_and_go():
            if hasattr(loading_window, 'cancelled') and loading_window.cancelled:
                return
            shifts = generate_shifts(dict(availability), weekly_shifts)
            while not shifts:
                if hasattr(loading_window, 'cancelled') and loading_window.cancelled:
                    return
                shifts = generate_shifts(dict(availability), weekly_shifts)
                loading_window.update()
            if loading_window.winfo_exists():
                loading_window.destroy()
                create_gui(shifts, weekly_shifts, availability)
        loading_window.after(100, calculate_and_go)
        loading_window.mainloop()
    
    # Handle window closing
    def on_closing():
        dialog.destroy()
    
    dialog.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Replace the original confirm button frame with two new buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=2, column=0, sticky='ew', pady=(0, 10))
    button_frame.grid_columnconfigure(0, weight=1)

    ttk.Button(button_frame, text="Apri Disponibilità",
               command=open_gui_availability_only, style='Accent.TButton',
               padding=(20, 10))\
        .grid(row=0, column=0, padx=5, pady=5)

    ttk.Button(button_frame, text="Genera Turni",
               command=open_gui_with_shifts, style='Accent.TButton',
               padding=(20, 10))\
        .grid(row=0, column=1, padx=5, pady=5)
    
    # Configure style for accent button
    style = ttk.Style()
    style.configure('Accent.TButton', font=('Helvetica', 10, 'bold'))
    
    dialog.mainloop()
    return not dialog.cancelled  # Return True if parameters were set, False if cancelled

# function to generate weekly shifts
def generate_shifts(availability, weekly_shifts):
    # create empty list for shifts
    shifts = []
    
    # loop through weekdays
    for day in weekly_shifts:
        # initialize random seed with different number each time
        random.seed(time.time_ns())

        # create empty list for available people on a specific day
        available_people = []
        
        # loop through available people
        for person in availability:
            # if person is available that day, add to available people list
            if day in availability[person]:
                available_people.append(person)
        
        # random selection of people for shift, return error if not enough available
        if len(available_people) >= MIN_PEOPLE_PER_SHIFT:
            shift = random.sample(
                available_people,
                random.randint(MIN_PEOPLE_PER_SHIFT,
                               min(MAX_PEOPLE_PER_SHIFT, len(available_people)))
            )
        else:
            return []
        
        # remove selected people from availability lists
        for person in shift:
            availability.pop(person)
        
        # add shift to shifts list
        shifts.append((day, shift))

    # return error if not all people were assigned to a shift
    if len(availability) != 0:
        return []

    return shifts

# function to load availability from csv file
def load_availability_from_csv(file_name, weekly_shifts):
    # create empty dictionary for availability
    availability = {}

    # open file for reading
    with open(file_name, 'r') as f:
        # read file content as CSV dictionary
        reader = csv.DictReader(f)
        
        # loop through file rows
        for row in reader:
            # extract person name and availability
            person = row['Nome']

            person_availability = []

            for shift in weekly_shifts:
                if row[shift].lower() == 'si':
                    person_availability.append(shift)
            
            # add availability to dictionary
            availability[person] = person_availability

    return availability

def create_gui(shifts, weekly_shifts, availability):
    root = tk.Tk()
    root.title("Turni Settimanali")
    
    # Set minimum window size
    root.minsize(800, 600)
    
    # Configure window size and position
    window_width = 1000  # Adjusted width
    window_height = 800
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Configure main window grid
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    
    # Main container frame
    container = ttk.Frame(root)
    container.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
    
    # Configure container grid
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=4)  # Adjusted weight
    container.grid_columnconfigure(1, weight=1)  # Right panel gets less space
    
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
    slot_labels = {'m': 'Mattina', 'pr': 'Pranzo', 'po': 'Pomeriggio'}  # Shorter labels

    # Configure grid weights to allow separator expansion
    total_rows = len(slots) * 2 + 2
    total_cols = len(days) * 2 + 1
    
    for i in range(total_rows):
        frame.grid_rowconfigure(i, weight=1, minsize=15)
    for j in range(total_cols):
        frame.grid_columnconfigure(j, weight=1, minsize=15)

    # Create more compact headers with abbreviated days
    for j, day in enumerate(days):
        header = tk.Label(frame, text=day.capitalize(),
                         fg="white", 
                         font=('Helvetica', 8, 'bold'),  # Smaller font
                         pady=3,
                         padx=1)
        header.grid(row=0, column=j*2 + 1, sticky='nsew')
    
    for i, slot in enumerate(slots):
        header = tk.Label(frame, text=slot_labels[slot],
                         fg="white",
                         font=('Helvetica', 8, 'bold'),  # Smaller font
                         padx=2, )
        header.grid(row=i*2 + 1, column=0, sticky='nsew')

    # Adjust separators spacing
    # for j in range(len(days) - 1):
    #     separator = ttk.Separator(frame, orient='vertical')
    #     separator.grid(row=0, column=j*2 + 2, rowspan=total_rows, sticky='ns', padx=5)

    # for i in range(len(slots) - 1):
    #     separator = ttk.Separator(frame, orient='horizontal')
    #     separator.grid(row=i*2 + 2, column=0, columnspan=total_cols, sticky='ew', pady=5)

    # Create a 3x5 grid with assigned people
    checkboxes = {}
    cell_frames = {}  # Store references to cell frames for updating colors
    
    indicators = {}  # Store references to indicators for updating colors

    def create_indicator(parent):
        canvas = tk.Canvas(parent, width=120, height=12, highlightthickness=0)  # Adjusted width
        rectangle = canvas.create_rectangle(0, 0, 120, 12, fill='#ffff33')  # Adjusted width
        return canvas, rectangle

    def validate_slot(slot):
        # Explicitly count only True values
        checked_count = sum(
            1 for (p, s), var in checkboxes.items()
            if s == slot and var.get() is True
        )
        if checked_count < MIN_PEOPLE_PER_SHIFT:
            return '#ffff33'  # Yellow
        elif checked_count > MAX_PEOPLE_PER_SHIFT:
            return '#ff0000'  # Red
        else:
            return '#66ff66'  # Green

    def update_slot_color(slot):
        color = validate_slot(slot)
        canvas, circle = indicators[slot]
        canvas.itemconfig(circle, fill=color)

    def get_unassigned_people():
        assigned = set()
        for (persona, slot), var in checkboxes.items():
            if var.get():
                assigned.add(persona)
        return sorted(set(availability.keys()) - assigned)

    def update_unassigned_list():
        unassigned_list.delete(0, tk.END)
        unassigned = get_unassigned_people()
        for person in unassigned:
            unassigned_list.insert(tk.END, person)
        # Update background color based on whether there are unassigned people
        if unassigned:
            unassigned_list.configure(bg='#ff0000')  # Light red if there are unassigned people
        else:
            unassigned_list.configure(bg='#66ff66')  # Light green if everyone is assigned

    def on_checkbox_change(persona, current_slot):
        if checkboxes[(persona, current_slot)].get():
            # Uncheck other slots for this person
            for slot in weekly_shifts:
                if slot != current_slot and (persona, slot) in checkboxes:
                    checkboxes[(persona, slot)].set(False)
                    # Update color for the other slots that we unchecked
                    update_slot_color(slot)
        # Update color for current slot
        update_slot_color(current_slot)
        update_unassigned_list()  # Update unassigned list after each change

    for i, slot in enumerate(slots):
        for j, day in enumerate(days):
            day_slot = f"{day}_{slot}"
            assigned_people = [
                p for g, t in shifts if g == day_slot for p in t
            ]
            available_people = [
                p for p, ds in availability.items() if day_slot in ds
            ]
            all_people = sorted(set(assigned_people) | set(available_people))

            cell_frame = tk.Frame(frame, relief="solid", borderwidth=1)
            cell_frame.grid(
                row=i*2 + 1, column=j*2 + 1, sticky='nsew',
                padx=1, pady=1, ipadx=1, ipady=1
            )
            cell_frames[day_slot] = cell_frame

            # Create and place the indicator at the top of the cell
            indicator_canvas, indicator_circle = create_indicator(cell_frame)
            indicator_canvas.grid(row=0, column=0, sticky='ew', columnspan=2)  # span full width
            indicators[day_slot] = (indicator_canvas, indicator_circle)

            # Create a frame for checkboxes
            checkbox_frame = tk.Frame(cell_frame)
            checkbox_frame.grid(row=1, column=0, sticky='nsew')
            checkbox_frame.grid_columnconfigure(0, weight=1)  # Ensure checkboxes expand

            # Make checkboxes more compact
            for persona in all_people:
                var = tk.BooleanVar(value=(persona in assigned_people))
                check = tk.Checkbutton(
                    checkbox_frame, 
                    text=persona, 
                    variable=var,
                    command=lambda p=persona, s=day_slot: on_checkbox_change(p, s),
                    font=('Helvetica', 8),
                    wraplength=100,  # Limit text width for wrapping
                    justify='left'  # Align wrapped text to the left
                )
                check.grid(sticky='ew', padx=0, pady=0)  # Expand checkboxes horizontally
                checkboxes[(persona, day_slot)] = var
            
            # Initialize indicator color
            update_slot_color(day_slot)
            
    def recalculate_shifts():
        root.destroy()
        # Show loading screen and generate new shifts
        loading_window = show_loading_screen()
        
        def calculate_and_go():
            if hasattr(loading_window, 'cancelled') and loading_window.cancelled:
                return
            new_shifts = generate_shifts(dict(availability), weekly_shifts)
            while not new_shifts:
                if hasattr(loading_window, 'cancelled') and loading_window.cancelled:
                    return
                new_shifts = generate_shifts(dict(availability), weekly_shifts)
                loading_window.update()
            if loading_window.winfo_exists():
                loading_window.destroy()
                create_gui(new_shifts, weekly_shifts, availability)
        
        loading_window.after(100, calculate_and_go)
        loading_window.mainloop()

    def get_system_font():
        system = platform.system()
        if system == 'Windows':
            return 'arial.ttf'
        elif system == 'Darwin':  # macOS
            return '/System/Library/Fonts/Helvetica.ttc'
        else:  # Linux and others
            # Common paths for Linux systems
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

            # Draw grid lines
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
        command=recalculate_shifts, padding=(10, 5)
    )
    recalc_button.grid(row=0, column=0, padx=5)

    print_button = ttk.Button(
        button_frame, text="Salva Immagine",
        command=save_image, padding=(10, 5)
    )
    print_button.grid(row=0, column=1, padx=5)

    def go_back_to_parameters():
        root.destroy()
        main()  # Let main() handle parameter dialog as usual

    back_button = ttk.Button(
        button_frame, text="Indietro",
        command=go_back_to_parameters,
        padding=(10, 5)
    )
    back_button.grid(row=0, column=2, padx=5)

    update_unassigned_list()
    root.mainloop()

class LoadingScreen:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Turni Settimanali")
        self.window.config(cursor="arrow")
        
        # Set minimum window size
        self.window.minsize(300, 200)
        
        # Add cancelled flag and after_id
        self.cancelled = False
        self.after_id = None
        self.arc_start = 0
        
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
        main()
    
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

def show_loading_screen():
    return LoadingScreen()

def main():
    # Show parameters dialog first and check if it was cancelled
    if not show_parameters_dialog():
        return
    
    availability = load_availability_from_csv(CSV_FILE_PATH, weekly_shifts)
    
    # Show loading screen
    loading_window = show_loading_screen()
    
    # Function to handle calculation and transition
    def calculate_and_display_results():
        if hasattr(loading_window, 'cancelled') and loading_window.cancelled:
            return
        
        shifts = generate_shifts(dict(availability), weekly_shifts)
        
        while (len(shifts) == 0):
            if hasattr(loading_window, 'cancelled') and loading_window.cancelled:
                return
            shifts = generate_shifts(dict(availability), weekly_shifts)
            loading_window.update()  # Force update of the window
        
        if loading_window.winfo_exists():
            loading_window.destroy()
            create_gui(shifts, weekly_shifts, availability)
    
    # Schedule calculation after loading window is shown
    loading_window.after(100, calculate_and_display_results)
    loading_window.mainloop()

if __name__ == "__main__":
    main()
