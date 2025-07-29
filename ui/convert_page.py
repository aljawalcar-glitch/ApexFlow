# -*- coding: utf-8 -*-
"""
صفحة تحويل الملفات
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout
from .theme_aware_widget import make_theme_aware
from .ui_helpers import create_button, create_title

class ConvertPage(QWidget):
    """
    واجهة المستخدم الخاصة بوظائف التحويل المختلفة.
    """
    def __init__(self, operations_manager, parent=None):
        """
        :param operations_manager: مدير العمليات لتنفيذ التحويلات.
        """
        super().__init__(parent)
        self.operations_manager = operations_manager
        
        # جعل الويدجت متجاوبًا مع السمات
        self.theme_handler = make_theme_aware(self, "convert_page")

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # إضافة العنوان
        title = create_title("تحويل الملفات")
        layout.addWidget(title)

        # شبكة أزرار التحويل
        buttons_grid = QGridLayout()
        buttons_grid.setSpacing(15)

        # تعريف الأزرار والإجراءات المرتبطة بها - إنجليزي فقط
        convert_buttons = [
            ("PDF to Images", self.operations_manager.pdf_to_images),
            ("Images to PDF", self.operations_manager.images_to_pdf),
            ("Extract Text from PDF", self.operations_manager.pdf_to_text),
            ("Text to PDF", self.operations_manager.text_to_pdf)
        ]

        # إنشاء الأزرار وترتيبها في شبكة (2x2)
        for i, (text, action) in enumerate(convert_buttons):
            btn = create_button(text)
            btn.clicked.connect(action)
            
            row = i // 2
            col = i % 2
            buttons_grid.addWidget(btn, row, col)

        layout.addLayout(buttons_grid)
        layout.addStretch()
