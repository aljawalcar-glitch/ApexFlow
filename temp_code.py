    def create_diagnostics_system_info_tab(self):
        """≈‰‘«¡  »ÊÌ» „⁄·Ê„«  «·‰Ÿ«„"""
        tab = QWidget()
        apply_theme_style(tab, "widget")
        layout = QVBoxLayout(tab)

        # ≈‰‘«¡ ‘Ã—… ·⁄—÷ «·„⁄·Ê„« 
        self.diagnostics_system_tree = QTreeWidget()
        self.diagnostics_system_tree.setHeaderLabels([tr("property"), tr("value")])
        self.diagnostics_system_tree.setColumnWidth(0, 200)
        apply_theme_style(self.diagnostics_system_tree, "tree_widget")
        layout.addWidget(self.diagnostics_system_tree)

        # ≈÷«›… ⁄·«„… «· »ÊÌ»
        self.diagnostics_stack.addWidget(tab)

        # ≈‰‘«¡ «·“— «·Ã«‰»Ì ·· »ÊÌ»
        button = QPushButton(tr("system_information"))
        button.setCheckable(True)
        button.clicked.connect(lambda: self.on_diagnostics_step_clicked(0))
        button.setStyleSheet("text-align: right; padding: 8px;")
        apply_theme_style(button, "tab_button")
        self.diagnostics_buttons_widget.layout().addWidget(button)
        self.diagnostics_tab_buttons.append(button)

        #  ⁄ÌÌ‰ «·“— «·√Ê· ﬂ‰‘ÿ
        if len(self.diagnostics_tab_buttons) == 1:
            button.setChecked(True)