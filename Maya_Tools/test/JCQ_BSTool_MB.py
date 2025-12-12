from PySide2 import QtWidgets, QtCore

class MyWindow(QtWidgets.QDialog):
    def __init__(self):
        super(MyWindow, self).__init__()

        # 创建主窗口
        self.setWindowTitle("JCQ_BS image Viewer")
        self.resize(600, 400)

        layout = QtWidgets.QGridLayout()

        # 创建Manual按钮
        manual_button = QtWidgets.QPushButton("Manual")
        manual_button.setFixedWidth(100)  # 设置按钮宽度为100
        layout.addWidget(manual_button, 0, 0, 1, 1, QtCore.Qt.AlignLeft)

        # 创建下拉列表1
        self.project_option_menu = QtWidgets.QComboBox()
        self.project_option_menu.currentIndexChanged.connect(self.update_sheet_list)
        layout.addWidget(QtWidgets.QLabel("Select Project"), 1, 0)
        layout.addWidget(self.project_option_menu, 1, 1)

        # 创建下拉列表2
        self.sheet_list = QtWidgets.QComboBox()
        layout.addWidget(QtWidgets.QLabel("Select List"), 2, 0)
        layout.addWidget(self.sheet_list, 2, 1)

        # 创建水平布局
        namespace_layout = QtWidgets.QHBoxLayout()

        # 创建左侧文本
        namespace_label = QtWidgets.QLabel("Namespace")
        namespace_layout.addWidget(namespace_label)

        # 创建右侧可编辑文本框
        self.namespace_line_edit = QtWidgets.QLineEdit()
        namespace_layout.addWidget(self.namespace_line_edit)

        layout.addLayout(namespace_layout, 3, 0, 1, 2)

        # 创建按钮并绑定函数
        create_button = QtWidgets.QPushButton("Create Tab")
        create_button.clicked.connect(self.create_labels)
        layout.addWidget(create_button, 4, 0, 1, 1)

        # 创建AR Kit按钮
        ar_kit_button = QtWidgets.QPushButton("AR Kit")
        ar_kit_button.setFixedWidth(100)  # 设置按钮宽度为100
        layout.addWidget(ar_kit_button, 4, 1, 1, 1)

        # 创建空的Tab布局
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setTabPosition(QtWidgets.QTabWidget.West)  # 将标签位置设置为左侧
        layout.addWidget(self.tab_widget, 5, 0, 1, 2)

        self.setLayout(layout)

    def update_sheet_list(self):
        selected_project = self.project_option_menu.currentText()
        # TODO: 实现获取项目列表的功能，并更新下拉列表2的内容
        pass

    def create_labels(self):
        # 创建一个新的选项卡并添加到Tab布局中
        new_tab = QtWidgets.QWidget()
        self.tab_widget.addTab(new_tab, "New Tab")

def create_Window():
    global myWindow
    try:
        myWindow.close()  # 关闭现有窗口
    except:
        pass

    myWindow = MyWindow()
    myWindow.show()


create_Window()
