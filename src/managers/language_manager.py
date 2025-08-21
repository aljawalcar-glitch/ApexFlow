# -*- coding: utf-8 -*-
"""
LanguageManager for handling application-wide language and layout direction.
"""

from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import QApplication

from utils.settings import load_settings, update_setting

RTL_LANGUAGES = ["ar", "he", "fa", "ur"]

class LanguageManager(QObject):
    """
    A singleton manager for handling application language and layout direction.
    """
    _instance = None
    language_changed = Signal(str, Qt.LayoutDirection)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(LanguageManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            super().__init__()
            self._settings = load_settings()
            self.current_language = self._settings.get("language", "ar")
            self._initialized = True

    def get_language(self):
        """Returns the current language code."""
        return self.current_language

    def set_language(self, lang_code):
        """Sets the application language and notifies subscribers."""
        if lang_code != self.current_language:
            self.current_language = lang_code
            update_setting("language", lang_code)

            # Apply direction first
            self.apply_application_direction()

            # Reload translations (only if app is initialized)
            app = QApplication.instance()
            if app:
                from utils.translator import reload_translations
                reload_translations(lang_code)

            # Emit signal to notify UI components
            self.language_changed.emit(self.current_language, self.get_direction())

    def get_direction(self):
        """Returns Qt.RightToLeft or Qt.LeftToRight based on the current language."""
        if self.current_language in RTL_LANGUAGES:
            return Qt.RightToLeft
        else:
            return Qt.LeftToRight

    def is_rtl(self):
        """Returns True if the current language is RTL."""
        return self.current_language in RTL_LANGUAGES

    def apply_application_direction(self):
        """Applies the layout direction to the entire application."""
        app = QApplication.instance()
        if app is not None:
            app.setLayoutDirection(self.get_direction())

    def tr(self, key, **kwargs):
        """Provides access to the translation function."""
        from utils.translator import tr as translator_tr
        return translator_tr(key, **kwargs)

# Global instance
language_manager = LanguageManager()
