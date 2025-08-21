# -*- coding: utf-8 -*-
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QLabel, QHBoxLayout
)
from PySide6.QtCore import Qt
from utils.i18n import tr
from managers.theme_manager import make_theme_aware

class SavePage(QWidget):
    def __init__(self, settings_data, parent_ui):
        super().__init__()
        self.settings_data = settings_data
        self.parent_ui = parent_ui
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # منطقة التقرير
        report_group = QGroupBox(tr("summary_of_changes_group"))
        make_theme_aware(report_group, "group_box")
        report_layout = QVBoxLayout(report_group)
        report_layout.setSpacing(10)

        self.changes_report = self.parent_ui.changes_report
        self.changes_report.setWordWrap(True)
        self.changes_report.setAlignment(Qt.AlignTop)
        report_layout.addWidget(self.changes_report)

        layout.addWidget(report_group)

        # جميع الأزرار على نفس الخط
        buttons_layout = QHBoxLayout()
        
        # زر إرجاع الافتراضية
        self.reset_defaults_btn = self.parent_ui.reset_defaults_btn
        make_theme_aware(self.reset_defaults_btn, "warning_button")
        buttons_layout.addWidget(self.reset_defaults_btn)
        
        # زر حفظ فقط
        self.save_only_btn = self.parent_ui.save_only_btn
        make_theme_aware(self.save_only_btn, "success_button")
        buttons_layout.addWidget(self.save_only_btn)
        
        # زر حفظ وإعادة تشغيل
        self.save_restart_btn = self.parent_ui.save_restart_btn
        make_theme_aware(self.save_restart_btn, "success_button")
        buttons_layout.addWidget(self.save_restart_btn)
        
        buttons_layout.addStretch()
        
        # زر الإلغاء
        self.cancel_btn = self.parent_ui.cancel_btn
        make_theme_aware(self.cancel_btn, "danger_button")
        buttons_layout.addWidget(self.cancel_btn)
        
        # إضافة التخطيط
        layout.addLayout(buttons_layout)
        layout.addStretch()
