"""
مجلد واجهة المستخدم - UI Package
يحتوي على جميع عناصر الواجهة والتصميم

تم تحسين هذا الملف لاستخدام التحميل الكسول (Lazy Loading) لتسريع بدء التطبيق.
عناصر الواجهة الثقيلة لن يتم تحميلها إلا عند الحاجة الفعلية.
"""

# لا نستورد أي عناصر واجهة ثقيلة هنا لضمان بدء تشغيل سريع
# سيتم تحميل العناصر عند الحاجة

def __getattr__(name):
    """
    تحميل كسول لعناصر الواجهة عند الطلب
    هذا يضمن عدم تحميل العناصر الثقيلة إلا عند الحاجة
    """
    # عناصر الواجهة الرئيسية
    if name == 'WelcomePage':
        from .WelcomePage import WelcomePage
        globals()['WelcomePage'] = WelcomePage
        return WelcomePage

    elif name == 'FileListFrame':
        from .file_list_frame import FileListFrame
        globals()['FileListFrame'] = FileListFrame
        return FileListFrame

    elif name == 'SettingsUI':
        from .settings_ui import SettingsUI
        globals()['SettingsUI'] = SettingsUI
        return SettingsUI

    elif name in ['SVGIconButton', 'create_navigation_button', 'create_rotation_button', 'create_action_button']:
        from .svg_icon_button import SVGIconButton, create_navigation_button, create_rotation_button, create_action_button
        globals().update({
            'SVGIconButton': SVGIconButton,
            'create_navigation_button': create_navigation_button,
            'create_rotation_button': create_rotation_button,
            'create_action_button': create_action_button
        })
        return globals()[name]

    elif name == 'AppInfoWidget':
        from .app_info_widget import AppInfoWidget
        globals()['AppInfoWidget'] = AppInfoWidget
        return AppInfoWidget

    # أدوات التصميم (خفيفة، يمكن تحميلها مباشرة)
    elif name in ['get_button_style', 'get_menu_style', 'get_scroll_style', 'get_combo_style',
                  'get_input_style', 'hex_to_rgba', 'adjust_color_brightness']:
        from .ui_helpers import (get_button_style, get_menu_style, get_scroll_style,
                                get_combo_style, get_input_style, hex_to_rgba, adjust_color_brightness)
        globals().update({
            'get_button_style': get_button_style,
            'get_menu_style': get_menu_style,
            'get_scroll_style': get_scroll_style,
            'get_combo_style': get_combo_style,
            'get_input_style': get_input_style,
            'hex_to_rgba': hex_to_rgba,
            'adjust_color_brightness': adjust_color_brightness
        })
        return globals()[name]

    elif name == 'darken_color':
        from .global_styles import darken_color
        globals()['darken_color'] = darken_color
        return darken_color

    # نظام السمات (مهم، لكن يمكن تحميله عند الطلب)
    elif name in ['apply_theme_style', 'global_theme_manager']:
        from .theme_manager import apply_theme_style, global_theme_manager
        globals().update({
            'apply_theme_style': apply_theme_style,
            'global_theme_manager': global_theme_manager
        })
        return globals()[name]

    elif name in ['make_theme_aware', 'ThemeAwareMainWindow']:
        from .theme_aware_widget import make_theme_aware, ThemeAwareMainWindow
        globals().update({
            'make_theme_aware': make_theme_aware,
            'ThemeAwareMainWindow': ThemeAwareMainWindow
        })
        return globals()[name]

    elif name == 'apply_global_style':
        from .global_styles import apply_global_style
        globals()['apply_global_style'] = apply_global_style
        return apply_global_style

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

# تم حذف أدوات النصوص المختلطة - الحلول المعقدة غير مجدية

__all__ = [
    # عناصر الواجهة
    'WelcomePage',
    'FileListFrame',
    'SettingsUI',
    'SVGIconButton',
    'create_navigation_button',
    'create_rotation_button',
    'create_action_button',
    'AppInfoWidget',

    # أدوات التصميم
    'get_button_style',
    'get_menu_style',
    'get_scroll_style',
    'get_combo_style',
    'get_input_style',
    'hex_to_rgba',
    'adjust_color_brightness',

    # نظام السمات
    'apply_theme_style',
    'global_theme_manager',
    'make_theme_aware',
    'ThemeAwareMainWindow',
    'apply_global_style',
]