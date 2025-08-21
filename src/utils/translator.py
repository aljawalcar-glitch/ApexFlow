# -*- coding: utf-8 -*-
"""
Module for handling application translations.
وحدة للتعامل مع ترجمات التطبيق.
"""
import json
import os
from .logger import error
# تأجيل الاستيراد لتجنب circular import
# from managers.language_manager import language_manager

class Translator:
    """
    A simple translator class that loads strings from a JSON file.
    """
    def __init__(self):
        self.translations = {}
        self.language = 'ar'  # افتراضي
        self.load_translations()

    def load_translations(self, lang_code=None):
        """
        Loads the translation file based on the current language setting.
        """
        try:
            if lang_code is None:
                try:
                    from managers.language_manager import language_manager
                    lang_code = language_manager.get_language()
                except ImportError:
                    lang_code = 'ar'  # افتراضي
            
            self.language = lang_code
            
            # مسار ملف الترجمة
            translations_file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'translations.json')

            if os.path.exists(translations_file_path):
                with open(translations_file_path, 'r', encoding='utf-8') as f:
                    all_translations = json.load(f)
                
                self.translations = all_translations.get(self.language, {})
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
    result = translator.tr(key, **kwargs)
    # إذا كانت النتيجة هي نفس المفتاح، حاول إعادة تحميل الترجمات
    if result == key and len(translator.translations) == 0:
        translator.load_translations()
        result = translator.tr(key, **kwargs)
    return result

def get_current_language() -> str:
    """
    Returns the current language code.
    إرجاع رمز اللغة الحالية.
    """
    try:
        from managers.language_manager import language_manager
        return language_manager.get_language()
    except ImportError:
        return 'ar'

def reload_translations(lang_code):
    """
    Reloads translations for the given language code.
    """
    translator.load_translations(lang_code)
