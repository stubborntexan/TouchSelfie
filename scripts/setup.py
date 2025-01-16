"""
Graphical and Command-line setup scripts for TouchSelfie

This script is an assistant that guides users
through the process of configuring wanted features
and optionally
    - creating a Google Project to allow OAuth2 authentication
    - creating the configuration.json file
    - creating the startup script photobooth.sh
"""

import os
import sys
import configuration
import constants
import mykb
import cups  # Ensure CUPS is installed on your Raspberry Pi
from tkinter import *
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog
from PIL import Image as _Image
from PIL import ImageTk as _ImageTk

# URL of the Google console developer assistant to create App_id file
GET_APP_ID_WIZARD_URL = "https://console.developers.google.com/start/api?id=gmail"

VALID_ICON_FILE = os.path.join("resources", "ic_valid.png")  # Fixed the directory name
INVALID_ICON_FILE = os.path.join("resources", "ic_invalid.png")  # Fixed the directory name

class Assistant(Tk):
    """A page-by-page assistant based on Tk"""
    BUTTONS_BG = '#4285f4'
    BUTTONS_BG_INACTIVE = 'white'
    BUTTONS_BG_ACTION = '#db4437'
    USE_SOFT_KEYBOARD = True

    def __init__(self, config, *args, **kwargs):
        """This creates all the widgets and variables"""
        super().__init__(*args, **kwargs)  # Use the super() function for inheritance
        self.google_service = None
        self.config = config
        self.printer_selection_enable = True  # CUPS printer selection
        self.packed_widgets = []
        self.page = 0
        self.setup_ui()

        # Handle CUPS
        try:
            conn = cups.Connection()
            self.printer_selection_enable = True
        except ImportError:
            print("CUPS not installed. Removing printer option.")
            self.printer_selection_enable = False

    def setup_ui(self):
        self.config(bg="white")
        self.main_frame = Frame(self, bg="white")
        self.buttons_frame = Frame(self, bg='white')

        self.b_next = Button(self.buttons_frame, text="Next", fg='white', bg=self.BUTTONS_BG,
                             width=10, command=self.__increment, font='Helvetica')
        self.b_prev = Button(self.buttons_frame, text="Prev", fg='white', bg=self.BUTTONS_BG,
                             width=10, command=self.__decrement, font='Helvetica')

        self.main_frame.pack(fill=X, ipadx=10, ipady=10)
        self.buttons_frame.pack(side=BOTTOM)
        self.b_prev.pack(side=LEFT, padx=40)
        self.b_next.pack(side=RIGHT, padx=40)

        # Variables
        self.create_variables()  # Moved the variable creation to a separate method
        self.widgets = []  # This should be cleared at initialization
        self.create_widgets()  # Create initial widgets

        # Draw the first page
        self.__draw_page()

    def create_variables(self):
        """Create Tkinter variables and their corresponding change handlers."""
        self.want_email_var = IntVar(value=self.config.enable_email)
        self.want_email_var.trace("w", lambda *args: self.update_config('enable_email', self.want_email_var.get()))

        self.want_upload_var = IntVar(value=self.config.enable_upload)
        self.want_upload_var.trace("w", lambda *args: self.update_config('enable_upload', self.want_upload_var.get()))

        self.want_effects_var = IntVar(value=self.config.enable_effects)
        self.want_effects_var.trace("w", lambda *args: self.update_config('enable_effects', self.want_effects_var.get()))

        if self.printer_selection_enable:
            self.want_print_var = IntVar(value=self.config.enable_print)
            self.want_print_var.trace("w", self.on_want_print_change)

        # for soft keyboard
        self.use_soft_keyboard_var = IntVar(value=0)
        self.use_soft_keyboard_var.trace("w", lambda *args: self.USE_SOFT_KEYBOARD == self.use_soft_keyboard_var.get() != 0)

    def update_config(self, attr_name, value):
        setattr(self.config, attr_name, value != 0)

    def create_widgets(self):
        """Create and place the main widgets in the frame."""
        # Email, upload, effects checkbuttons
        self.want_email_cb = Checkbutton(self.main_frame, text="Enable Email sending", variable=self.want_email_var, anchor=W, font='Helvetica')
        self.want_upload_cb = Checkbutton(self.main_frame, text="Enable photo upload", variable=self.want_upload_var, anchor=W, font='Helvetica')
        self.want_effects_cb = Checkbutton(self.main_frame, text="Enable image effects", variable=self.want_effects_var, anchor=W, font='Helvetica')

        if self.printer_selection_enable:
            self.want_print_cb = Checkbutton(self.main_frame, text="Enable photo print", variable=self.want_print_var, anchor=W, font='Helvetica')

        self.want_email_cb.pack()
        self.want_upload_cb.pack()
        self.want_effects_cb.pack()
        if self.printer_selection_enable:
            self.want_print_cb.pack()

    def on_want_print_change(self, *args):
        if self.want_print_var.get() != 0:  # If selected
            self.setup_printer_list()

    def setup_printer_list(self):
        """Set up the printer list using CUPS."""
        try:
            conn = cups.Connection()
            printers = conn.getPrinters()
            printers_list = Listbox(self.main_frame)
            printers_list.pack()

            for printer in printers:
                printers_list.insert(END, printer)

        except Exception as e:
            tkMessageBox.showerror("Printer Error", f"Failed to load printers: {str(e)}")
            self.want_print_var.set(0)  # Deselect printer option

    # Add the rest of your functions following the same structure...

    def __draw_page(self):
        """Pack all the widgets corresponding to the current page."""
        self.__erase_page()
        for widget in self.widgets[self.page]:
            widget.pack(fill=X, padx=20, pady=10)
            self.packed_widgets.append(widget)

        # Handle previous and next button states
        self.b_prev.config(state=NORMAL if self.page > 0 else DISABLED, bg=self.BUTTONS_BG if self.page > 0 else self.BUTTONS_BG_INACTIVE)
        self.b_next.config(text="Next" if self.page < len(self.widgets) - 1 else "Save", background=self.BUTTONS_BG_ACTION if self.page >= len(self.widgets) - 1 else self.BUTTONS_BG)

    def __erase_page(self):
        """Unpack all the widget currently displayed."""
        for widget in self.packed_widgets:
            widget.pack_forget()
        self.packed_widgets = []

    def __increment(self):
        """Increment by one page."""
        # Your logic for incrementing page number
        # Ensure that you implement logic to loop through pages correctly

    def __decrement(self):
        """Decrement by one page."""
        # Your logic for decrementing page number
        # Ensure that you implement logic to loop through pages correctly

def graphical_assistant():
    """Launches the graphical interface."""
    try:
        config = configuration.Configuration('configuration.json')
        root = Assistant(config)
        root.geometry("450x400")
        root.mainloop()
    except Exception as e:
        print(f"Graphical interface error: {e}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="TouchSelfie Setup Assistant")
    parser.add_argument("-c", "--console", help="console mode, no graphical interface", action="store_true")
    args = parser.parse_args()

    if args.console:
        console_assistant()  # Don't forget to implement this if required!
    else:
        graphical_assistant()
