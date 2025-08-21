# -*- coding: utf-8 -*-
"""
ويدجت تنظيف الملفات المؤقتة
Temp Files Cleaner Widget
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QProgressBar, QTextEdit, QGroupBox)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from src.managers.theme_manager import make_theme_aware
from src.utils.translator import tr
from src.utils.temp_cleaner import clean_temp_files, get_temp_directories
import os

class TempCleanerThread(QThread):
    """خيط تنظيف الملفات المؤقتة"""
    progress = Signal(str)
    finished = Signal(int, int)  # files_count, size_bytes
    
    def run(self):
        self.progress.emit(tr("scanning_temp_files"))
        files_count, size_bytes = clean_temp_files()
        self.finished.emit(files_count, size_bytes)

class TempCleanerWidget(QWidget):
    """ويدجت تنظيف الملفات المؤقتة"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # معلومات التنظيف
        info_group = QGroupBox(tr("temp_files_info"))
        make_theme_aware(info_group, "group_box")
        info_layout = QVBoxLayout(info_group)
        
        self.info_label = QLabel(tr("temp_files_description"))
        self.info_label.setWordWrap(True)
        info_layout.addWidget(self.info_label)
        
        # إحصائيات
        stats_layout = QHBoxLayout()
        self.files_label = QLabel(tr("temp_files_count", count=0))
        self.size_label = QLabel(tr("temp_files_size", size="0 MB"))
        stats_layout.addWidget(self.files_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self.size_label)
        info_layout.addLayout(stats_layout)
        
        layout.addWidget(info_group)
        
        # أزرار التحكم
        controls_layout = QHBoxLayout()
        
        self.scan_btn = QPushButton(tr("scan_temp_files"))
        self.scan_btn.clicked.connect(self.scan_temp_files)
        make_theme_aware(self.scan_btn, "button")
        
        self.clean_btn = QPushButton(tr("clean_temp_files"))
        self.clean_btn.clicked.connect(self.clean_temp_files)
        self.clean_btn.setEnabled(False)
        make_theme_aware(self.clean_btn, "success_button")
        
        controls_layout.addWidget(self.scan_btn)
        controls_layout.addWidget(self.clean_btn)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        make_theme_aware(self.progress_bar, "progress_bar")
        layout.addWidget(self.progress_bar)
        
        # تسجيل العمليات
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setReadOnly(True)
        make_theme_aware(self.log_text, "text_edit")
        layout.addWidget(self.log_text)
        
        # فحص أولي
        QTimer.singleShot(500, self.scan_temp_files)
    
    def scan_temp_files(self):
        """فحص الملفات المؤقتة"""
        self.scan_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # مؤشر غير محدد
        
        # حساب الملفات المؤقتة
        temp_count = 0
        temp_size = 0
        
        try:
            import glob
            from src.utils.temp_cleaner import get_dir_size
            
            temp_patterns = ["ApexFlow_*", "pdf_temp_*", "merge_temp_*", "split_temp_*", "compress_temp_*", "*.tmp"]
            
            for temp_dir in get_temp_directories():
                for pattern in temp_patterns:
                    files = glob.glob(os.path.join(temp_dir, pattern))
                    for file_path in files:
                        if os.path.exists(file_path):
                            temp_count += 1
                            if os.path.isfile(file_path):
                                temp_size += os.path.getsize(file_path)
                            elif os.path.isdir(file_path):
                                temp_size += get_dir_size(file_path)
        except Exception as e:
            self.log_text.append(f"خطأ في الفحص: {e}")
        
        # تحديث الواجهة
        self.files_label.setText(tr("temp_files_count", count=temp_count))
        size_mb = temp_size / (1024 * 1024)
        self.size_label.setText(tr("temp_files_size", size=f"{size_mb:.2f} MB"))
        
        self.clean_btn.setEnabled(temp_count > 0)
        self.scan_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if temp_count > 0:
            self.log_text.append(tr("scan_completed", count=temp_count, size=f"{size_mb:.2f} MB"))
        else:
            self.log_text.append(tr("no_temp_files_found"))
    
    def clean_temp_files(self):
        """تنظيف الملفات المؤقتة"""
        self.clean_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        # إنشاء خيط التنظيف
        self.cleaner_thread = TempCleanerThread()
        self.cleaner_thread.progress.connect(self.log_text.append)
        self.cleaner_thread.finished.connect(self.on_cleaning_finished)
        self.cleaner_thread.start()
    
    def on_cleaning_finished(self, files_count, size_bytes):
        """عند انتهاء التنظيف"""
        self.progress_bar.setVisible(False)
        
        if files_count > 0:
            size_mb = size_bytes / (1024 * 1024)
            self.log_text.append(tr("cleaning_completed", count=files_count, size=f"{size_mb:.2f} MB"))
        else:
            self.log_text.append(tr("no_files_cleaned"))
        
        # إعادة فحص
        QTimer.singleShot(1000, self.scan_temp_files)