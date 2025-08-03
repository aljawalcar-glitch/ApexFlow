def on_settings_chosen(language, theme):
    """Callback function for when settings are chosen in the first run dialog"""
    set_setting("language", language)
    set_setting("theme", theme)
    # Apply the theme
    from ui.theme_manager import set_theme
    set_theme(theme)
    # Apply the language
    from modules.translator import set_language
    set_language(language)

