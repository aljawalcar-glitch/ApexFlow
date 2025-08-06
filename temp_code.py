    def create_diagnostics_system_info_tab(self):
        """����� ����� ������� ������"""
        tab = QWidget()
        apply_theme_style(tab, "widget")
        layout = QVBoxLayout(tab)

        # ����� ���� ���� ���������
        self.diagnostics_system_tree = QTreeWidget()
        self.diagnostics_system_tree.setHeaderLabels([tr("property"), tr("value")])
        self.diagnostics_system_tree.setColumnWidth(0, 200)
        apply_theme_style(self.diagnostics_system_tree, "tree_widget")
        layout.addWidget(self.diagnostics_system_tree)

        # ����� ����� �������
        self.diagnostics_stack.addWidget(tab)

        # ����� ���� ������� �������
        button = QPushButton(tr("system_information"))
        button.setCheckable(True)
        button.clicked.connect(lambda: self.on_diagnostics_step_clicked(0))
        button.setStyleSheet("text-align: right; padding: 8px;")
        apply_theme_style(button, "tab_button")
        self.diagnostics_buttons_widget.layout().addWidget(button)
        self.diagnostics_tab_buttons.append(button)

        # ����� ���� ����� ����
        if len(self.diagnostics_tab_buttons) == 1:
            button.setChecked(True)