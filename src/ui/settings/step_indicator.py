# -*- coding: utf-8 -*-
"""
مؤشر الخطوات (Step Indicator)
"""
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout
from PySide6.QtCore import Signal
from managers.theme_manager import make_theme_aware
from utils.i18n import tr

class StepIndicator(QWidget):
    step_clicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_step = 0
        self.steps = [
            tr("step_appearance"),
            tr("step_fonts"),
            tr("step_general_settings"),
            tr("step_save")
        ]
        self._build_ui()

    def _build_ui(self):
        layout = QHBoxLayout(self)
        self.buttons = []
        for i, name in enumerate(self.steps):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, idx=i: self.step_clicked.emit(idx))
            make_theme_aware(btn, "tab_button")
            self.buttons.append(btn)
            layout.addWidget(btn)
        layout.addStretch()
        self.set_current_step(0)

    def set_current_step(self, step:int):
        self.current_step = step
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == step)

    def rebuild_ui(self):
        """إعادة بناء واجهة المستخدم لمؤشر الخطوات للتكيف مع تغييرات اللغة"""
        # مسح التخطيط الحالي بالكامل
        if self.layout() is not None:
            while self.layout().count():
                item = self.layout().takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        
        # إعادة إنشاء الواجهة
        self._build_ui()
        self.set_current_step(self.current_step)
