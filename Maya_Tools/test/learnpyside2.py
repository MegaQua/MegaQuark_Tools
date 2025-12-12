from PySide2 import QtWidgets
from pyfbsdk import FBTrace

class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MyWindow, self).__init__(None)

        self.setWindowTitle("Maya Window")

        # 创建按钮
        button = QtWidgets.QPushButton("Click Me")
        button.clicked.connect(self.button_clicked)

        # 创建布局
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(button)
        self.setLayout(layout)

        # 显示窗口
        self.show()

    def button_clicked(self):
        print("Button clicked!")
        FBTrace("Button clicked!\n")  # 将输出写入控制台

# 创建并自动显示窗口实例
window = MyWindow()
