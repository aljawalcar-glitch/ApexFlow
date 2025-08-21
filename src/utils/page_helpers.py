"""مساعدات الصفحات والتنقل"""

class PageHelpers:
    """مساعدات للتعامل مع الصفحات"""
    
    PAGE_MAPPING = {
        "merge": 1, "split": 2, "compress": 3, 
        "rotate": 4, "convert": 5, "security": 6
    }
    
    @staticmethod
    def get_page_index(action):
        """الحصول على فهرس الصفحة من الإجراء"""
        return PageHelpers.PAGE_MAPPING.get(action)
    
    @staticmethod
    def get_current_page_widget(main_window):
        """الحصول على ويدجت الصفحة الحالية"""
        current_index = main_window.stack.currentIndex()
        if current_index <= 0 or not main_window.pages_loaded[current_index]:
            return None, current_index
            
        current_page = main_window.stack.widget(current_index)
        if hasattr(current_page, 'widget'):
            current_page = current_page.widget()
        return current_page, current_index
    
    @staticmethod
    def add_files_to_page(page, files):
        """إضافة ملفات إلى صفحة"""
        if hasattr(page, 'add_files'):
            page.add_files(files)
            return True
        elif hasattr(page, 'file_list_frame') and hasattr(page.file_list_frame, 'add_files'):
            page.file_list_frame.add_files(files)
            return True
        return False
    
    @staticmethod
    def execute_page_action(page, action):
        """تنفيذ إجراء على صفحة"""
        action_methods = {
            "merge": "execute_merge",
            "split": "execute_split", 
            "compress": "execute_compress",
            "rotate": "execute_rotate",
            "convert": "execute_convert",
            "security": "execute_security"
        }
        
        method_name = action_methods.get(action)
        if method_name and hasattr(page, method_name):
            getattr(page, method_name)()
            return True
        return False