from PySide2 import QtWidgets, QtGui, QtCore
import maya.cmds as cmds
import maya.mel as mel
import re

class Toolkit(QtWidgets.QWidget):
    def __init__(self):
        super(Toolkit, self).__init__(None)

        self.setWindowTitle("Tool kit")

        # 创建一个选项卡部件
        self.tabs = QtWidgets.QTabWidget()

        TAB1 = True
        if TAB1:
            Tab1 = QtWidgets.QWidget()
            self.tabs.addTab(Tab1, "tab1")

            Tab1_Button1 = QtWidgets.QPushButton("Button1")
            # 创建日志框
            self.Tab1_log = QtWidgets.QTextEdit()
            self.Tab1_log.setReadOnly(True)
            self.Tab1_log.setMinimumHeight(120)

            # 连接按钮信号
            Tab1_Button1.clicked.connect(self.button_clicked)

            layout = QtWidgets.QVBoxLayout(Tab1)

            layout.addWidget(Tab1_Button1)
            layout.addWidget(self.Tab1_log)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.tabs)
        self.setLayout(mainLayout)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.show()

    def log_message(self, message, log_widget):
        """在指定日志控件里输出消息。
        - QTextEdit：旧文本置灰，新文本白色并追加
        - QPlainTextEdit：仅追加新文本（不改颜色）
        """
        if isinstance(log_widget, QtWidgets.QTextEdit):
            cursor = log_widget.textCursor()
            cursor.beginEditBlock()

            cursor.movePosition(QtGui.QTextCursor.Start)
            cursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.KeepAnchor)
            gray_fmt = QtGui.QTextCharFormat()
            gray_fmt.setForeground(QtGui.QColor("#888888"))
            cursor.setCharFormat(gray_fmt)

            cursor.movePosition(QtGui.QTextCursor.End)
            white_fmt = QtGui.QTextCharFormat()
            white_fmt.setForeground(QtGui.QColor("#ffffff"))
            cursor.setCharFormat(white_fmt)
            cursor.insertText(f"> {message}\n")

            cursor.endEditBlock()
            log_widget.moveCursor(QtGui.QTextCursor.End)
            return

        if isinstance(log_widget, QtWidgets.QPlainTextEdit):
            log_widget.appendPlainText(f"> {message}")
            log_widget.moveCursor(QtGui.QTextCursor.End)
            return

        try:
            log_widget.append(f"> {message}\n")
        except Exception:
            pass

    def button_clicked(self):
        button_text = self.sender().text()
        self.log_message(f"button '{button_text}' been clicked！", self.Tab1_log)

# 创建窗口实例
window = Toolkit()
