from src.app_config import AppConfig
from src.shift_utils import load_availability, generate_shifts
from src.loading_screen import LoadingScreen
from src.parameters_dialog import ParametersDialog
from src.shift_gui import ShiftGUI

class CUSLShiftApp:
    def __init__(self):
        self.config = AppConfig()

    def main(self):
        dialog_result = ParametersDialog(self.config).show()
        if not dialog_result[0]:  # If cancelled
            return
            
        self.availability = load_availability(
            self.config, self.config.CSV_FILE_PATH
        )
        
        if dialog_result[1]:  # If availability_only
            self.show_gui([])  # Pass empty shifts list
        else:
            self.show_loading_screen()  # Normal flow with shift generation

    def show_loading_screen(self):
        screen = LoadingScreen(on_cancel=self.main)
        screen.window.after(100, self.calculate_shifts, screen)
        screen.mainloop()

    def calculate_shifts(self, screen):
        shifts = generate_shifts(self.config, dict(self.availability))
        while not shifts and not screen.cancelled:
            shifts = generate_shifts(self.config, dict(self.availability))
            screen.update()
        if not screen.cancelled:
            screen.destroy()
            self.show_gui(shifts)

    def show_gui(self, shifts):
        gui = ShiftGUI(
            self.config,
            shifts,
            self.config.weekly_shifts,
            self.availability,
            self.main,
            self.calculate_shifts
        )
        gui.show()

if __name__ == "__main__":
    CUSLShiftApp().main()