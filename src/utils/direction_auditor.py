from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt
from managers.language_manager import language_manager

def audit_layout_directions():
    """
    Iterates through all widgets in the application and checks if their layout direction
    matches the application's global layout direction. This is useful for identifying
    widgets that might not be respecting the language manager's RTL/LTR settings.
    """
    app = QApplication.instance()
    if not app:
        print("[WARNING] QApplication instance not found. Cannot perform layout direction audit.")
        return

    global_direction = app.layoutDirection()
    lm_direction = language_manager.get_direction()
    lm_language = language_manager.get_language()

    print("--- Starting Layout Direction Audit ---")
    print(f"  - Language Manager State: lang='{lm_language}', expected_direction={lm_direction}")
    print(f"  - QApplication Global Direction: {global_direction}")

    def check_widget_recursive(widget: QWidget):
        # Check the widget itself
        if widget.layoutDirection() != global_direction:
            widget_name = widget.objectName() or widget.__class__.__name__
            print(
                f"[DIRECTION MISMATCH] Widget '{widget_name}' "
                f"has direction {widget.layoutDirection()} "
                f"instead of global {global_direction}."
            )

        # Recurse through children
        # Using findChildren directly can be simpler and more robust
        # for child in widget.findChildren(QWidget, options=Qt.FindDirectChildrenOnly):
        #    check_widget_recursive(child)
    
    # We only need to check top-level widgets, and then findChildren will do the rest.
    # However, a simpler approach is to get all widgets and check them.
    all_widgets = app.allWidgets()
    for widget in all_widgets:
        # We check the widget's own layoutDirection property.
        # The `layoutDirection` property is not inherited automatically in the same way
        # as it is for child widgets within a layout. We need to check each one.
        if widget.layoutDirection() != global_direction:
            widget_name = widget.objectName() or widget.__class__.__name__
            print(
                f"[DIRECTION MISMATCH] Widget '{widget_name}' "
                f"has direction {widget.layoutDirection()} "
                f"instead of global {global_direction}."
            )


    print("--- Layout Direction Audit Finished ---")
