# -*- coding: utf-8 -*-
"""
Module for handling application translations.
وحدة للتعامل مع ترجمات التطبيق.
"""
import json
import os
from .settings import load_settings
from .logger import debug, error

class Translator:
    """
    A simple translator class that loads strings from a JSON file.
    """
    def __init__(self):
        self.translations = {}
        self.language = "ar"
        self.load_translations()

    def load_translations(self):
        """
        Loads the translation file based on the current language setting.
        """
        try:
            settings = load_settings()
            self.language = settings.get("language", "ar")
            
            # مسار ملف الترجمة
            translations_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'translations.json')

            if os.path.exists(translations_file_path):
                with open(translations_file_path, 'r', encoding='utf-8') as f:
                    all_translations = json.load(f)
                
                self.translations = all_translations.get(self.language, {})
                debug(f"Loaded translations for language: {self.language}")
            else:
                error(f"Translation file not found at: {translations_file_path}")
                self.translations = {}

        except Exception as e:
            error(f"Failed to load translations: {e}")
            self.translations = {}

    def tr(self, key: str, **kwargs) -> str:
        """
        Gets the translated string for a given key.
        
        Args:
            key (str): The key for the string to translate.
            **kwargs: Placeholder values to format into the string.
            
        Returns:
            str: The translated and formatted string, or the key if not found.
        """
        # الحصول على النص المترجم، أو إرجاع المفتاح نفسه كقيمة افتراضية
        template = self.translations.get(key, key)
        
        # تعويض المتغيرات إذا وجدت
        try:
            return template.format(**kwargs)
        except KeyError as e:
            error(f"Placeholder key missing in translation for '{key}': {e}")
            return template # إرجاع القالب غير المنسق في حالة الخطأ

# --- المثيل العالمي للترجمة ---
# يتم إنشاؤه مرة واحدة ويتم استيراده في الوحدات الأخرى
translator = Translator()

def tr(key: str, **kwargs) -> str:
    """
    Shortcut function to access the global translator instance.
    دالة مختصرة للوصول إلى مثيل المترجم العالمي.
    """
    return translator.tr(key, **kwargs)
