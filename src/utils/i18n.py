# -*- coding: utf-8 -*-
"""
Global translation accessor.
"""

def tr(key, **kwargs):
    """
    A global shortcut to the LanguageManager's translation function.
    This makes it easier to call translations from anywhere in the UI code
    without needing to import the manager instance directly.

    Args:
        key (str): The translation key.
        **kwargs: Placeholder values for formatted strings.

    Returns:
        str: The translated and formatted string.
    """
    # Local import to avoid circular dependencies at startup
    from managers.language_manager import language_manager
    return language_manager.tr(key, **kwargs)
