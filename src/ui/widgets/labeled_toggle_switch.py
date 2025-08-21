# -*- coding: utf-8 -*-
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtCore import Signal
from src.ui.widgets.toggle_switch import ToggleSwitch

class LabeledToggleSwitch(QWidget):
    stateChanged = Signal(int)

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.label = QLabel(text)
        self.label.setStyleSheet("border: none;")
        self.toggle = ToggleSwitch()
        
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.toggle)
        
        self.toggle.stateChanged.connect(self.stateChanged.emit)

    def isChecked(self):
        return self.toggle.isChecked()

    def setChecked(self, checked):
        self.toggle.setChecked(checked)
