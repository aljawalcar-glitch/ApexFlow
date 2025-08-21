from PySide6.QtWidgets import QStackedWidget, QGraphicsOpacityEffect
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QSequentialAnimationGroup, Qt, QTimer, Signal

class AnimatedStackedWidget(QStackedWidget):
    animationFinished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.m_speed = 150  # Animation speed in milliseconds
        self.m_animation_type = QEasingCurve.InOutQuad
        self.m_active = False
        self.m_next_index = -1

    def set_speed(self, speed):
        self.m_speed = speed

    def set_animation(self, animation_type):
        self.m_animation_type = animation_type

    def fade_to_index(self, index):
        if self.m_active or index == self.currentIndex():
            return

        self.m_active = True
        self.m_next_index = index
        
        current_widget = self.currentWidget()
        next_widget = self.widget(index)

        # Ensure widgets are valid
        if not current_widget or not next_widget:
            self.setCurrentIndex(index)
            self.m_active = False
            return

        # Set up opacity effects
        current_opacity = QGraphicsOpacityEffect(current_widget)
        current_widget.setGraphicsEffect(current_opacity)
        
        next_opacity = QGraphicsOpacityEffect(next_widget)
        next_widget.setGraphicsEffect(next_opacity)
        next_opacity.setOpacity(0.0)

        # Fade out current widget
        anim_out = QPropertyAnimation(current_opacity, b"opacity")
        anim_out.setDuration(self.m_speed // 2)
        anim_out.setEasingCurve(self.m_animation_type)
        anim_out.setStartValue(1.0)
        anim_out.setEndValue(0.0)

        # Fade in next widget
        anim_in = QPropertyAnimation(next_opacity, b"opacity")
        anim_in.setDuration(self.m_speed // 2)
        anim_in.setEasingCurve(self.m_animation_type)
        anim_in.setStartValue(0.0)
        anim_in.setEndValue(1.0)

        # Set up sequential animation
        self.animation_group = QSequentialAnimationGroup(self)
        self.animation_group.addAnimation(anim_out)
        self.animation_group.addAnimation(anim_in)

        # Connect signals
        anim_out.finished.connect(self.switch_page)
        self.animation_group.finished.connect(self.animation_done)

        self.animation_group.start()

    def switch_page(self):
        self.setCurrentIndex(self.m_next_index)

    def animation_done(self):
        # Clean up graphics effects after a short delay
        QTimer.singleShot(50, self.cleanup_effects)
        self.m_active = False
        self.animationFinished.emit()

    def cleanup_effects(self):
        for i in range(self.count()):
            widget = self.widget(i)
            if widget and widget.graphicsEffect():
                widget.setGraphicsEffect(None)
