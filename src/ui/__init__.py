"""
User Interface Module
وحدة واجهة المستخدم
"""

from .pages.WelcomePage import WelcomePage
from .pages.merge_page import MergePage
from .pages.split_page import SplitPage
from .pages.compress_page import CompressPage
from .pages.convert_page import ConvertPage
from .pages.rotate_page import RotatePage
from .pages.security_page import SecurityPage
from .pages.settings_ui import SettingsUI
from .pages.help_page import HelpPage

__all__ = [
    # Pages
    'WelcomePage', 'MergePage', 'SplitPage', 'CompressPage', 'ConvertPage', 
    'RotatePage', 'SecurityPage', 'SettingsUI', 'HelpPage'
]
