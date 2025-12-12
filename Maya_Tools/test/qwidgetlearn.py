from PySide2 import QtWidgets


class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MyWindow, self).__init__(None)

        self.setWindowTitle("Maya Window")

        # 创建按钮
        button = QtWidgets.QPushButton("Click Me", self)
        button.clicked.connect(self.button_clicked)

        # 创建布局
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(button)
        self.setLayout(layout)
        self.show()

    def button_clicked(self):
        print("Button clicked!")


# 创建窗口实例
window = MyWindow()