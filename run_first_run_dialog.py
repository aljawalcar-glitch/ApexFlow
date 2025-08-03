# -*- coding: utf-8 -*-
"""
Script to run the First Run Dialog
"""
import sys
from PySide6.QtWidgets import QApplication
from ui.first_run_dialog import FirstRunDialog

def main():
    app = QApplication(sys.argv)

    # Create and show the first run dialog
    dialog = FirstRunDialog()
    dialog.show()

    # Connect to the settings chosen signal
    def on_settings_chosen(language, theme):
        print(f"Language: {language}, Theme: {theme}")
        app.quit()

    dialog.settings_chosen.connect(on_settings_chosen)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
