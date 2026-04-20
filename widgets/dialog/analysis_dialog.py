from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtWidgets import QDialog, QGridLayout, QLayout, QRadioButton, QDialogButtonBox, QPushButton, \
    QHBoxLayout, QButtonGroup


class AnalysisDialog(QDialog):

    confirm_clicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("模版选择")
        self.setStyleSheet("""
            background-color: #ffffff;
        """)

        # radio button
        self.top_layout = QHBoxLayout()
        self.button_group = QButtonGroup()
        attendance_btn = QRadioButton("考勤模版(默认)")
        attendance_btn.setChecked(True)
        finance_btn = QRadioButton("财务模版")
        none_btn = QRadioButton("无模版")
        self.button_group.addButton(attendance_btn, 1)
        self.button_group.addButton(finance_btn, 2)
        self.button_group.addButton(none_btn, 3)
        self.top_layout.addWidget(attendance_btn)
        self.top_layout.addWidget(finance_btn)
        self.top_layout.addWidget(none_btn)

        # dialog button
        confirm_button = QPushButton("确认")
        confirm_button.setDefault(True)
        confirm_button.clicked.connect(self.confirm)
        more_button = QPushButton("更多")
        more_button.setEnabled(False)
        button_box = QDialogButtonBox(Qt.Orientation.Horizontal)
        button_box.addButton(more_button, QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(confirm_button, QDialogButtonBox.ButtonRole.ActionRole)

        main_layout = QGridLayout(self)
        main_layout.setSizeConstraint(QLayout.SizeConstraint.SetFixedSize)
        main_layout.addLayout(self.top_layout, 1, 0)
        main_layout.addWidget(button_box, 2, 0)

    def confirm(self, args):
        self.close()
        self.confirm_clicked.emit(self.button_group.checkedId())

    def reset(self):
        for i in range(1, 3):
            if i == 1:
                self.button_group.button(i).setChecked(True)
            else:
                self.button_group.button(i).setChecked(False)
