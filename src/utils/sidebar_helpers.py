"""مساعدات الشريط الجانبي"""
from PySide6.QtWidgets import QListWidgetItem
from PySide6.QtGui import QIcon

class SidebarHelpers:
    """مساعدات لإدارة الشريط الجانبي"""
    
    MENU_DATA = [
        ("menu_home", "logo"),
        ("menu_merge_print", "merge"),
        ("menu_split", "scissors"),
        ("menu_compress", "archive"),
        ("menu_stamp_rotate", "rotate-cw"),
        ("menu_convert", "file-text"),
        ("menu_security", "eye-off"),
        ("menu_settings", "settings"),
        ("menu_help", "info")
    ]
    
    @staticmethod
    def update_menu_items(menu_list):
        """تحديث عناصر القائمة"""
        menu_list.clear()
        
        try:
            from ui.widgets.svg_icon_button import create_colored_icon
            from utils.translator import tr
            from ui.widgets.ui_helpers import get_icon_path
        except ImportError:
            return False
        
        for text_key, icon_name in SidebarHelpers.MENU_DATA:
            colored_icon = create_colored_icon(icon_name, 24)
            if colored_icon:
                item = QListWidgetItem(colored_icon, tr(text_key))
            else:
                icon_path = get_icon_path(icon_name)
                item = QListWidgetItem(QIcon(icon_path), tr(text_key))
            menu_list.addItem(item)
        
        return True