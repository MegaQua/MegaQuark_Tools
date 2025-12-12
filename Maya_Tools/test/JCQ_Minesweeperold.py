import random
from PySide2 import QtWidgets, QtCore, QtGui


class Minesweeper(QtWidgets.QWidget):
    def __init__(self):
        super(Minesweeper, self).__init__(None)

        self.setWindowTitle("JCQ_Minesweeper")

        # 创建按钮和编号列表
        self.buttons = []
        self.button_numbers = []
        self.random_numbers = random.sample(range(1, 101), 15)
        self.open_count =0
        self.minecount = 0
        for i in range(1, 101):
            button = QtWidgets.QPushButton(self)
            button.setFixedSize(30, 30)
            button.clicked.connect(self.button_clicked)
            button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            button.customContextMenuRequested.connect(self.button_context_menu)
            self.buttons.append(button)
            self.button_numbers.append(i)

        # 创建布局
        layout = QtWidgets.QGridLayout()
        for i, button in enumerate(self.buttons):
            layout.addWidget(button, i // 10, i % 10)
        self.setLayout(layout)
        self.show()
    def titletextupdate(self):
        self.setWindowTitle("JCQ_Minesweeper"+" mime left "+ str(15-self.minecount))
        if self.minecount == 15 and self.open_count == 85:
            self.setWindowTitle("JCQ_Minesweeper____" + (" you win!!"))

    def button_clicked(self):
        button = self.sender()
        button_index = self.buttons.index(button)
        button_number = self.button_numbers[button_index]

        if button_number in self.random_numbers:
            button.setText('*')
            button.setEnabled(False)
            #button.setStyleSheet("background-color: red","color: black")
            self.set_button_color(button, QtGui.QColor("red"))
            self.setWindowTitle("JCQ_Minesweeper____" + (" you lose"))
        else:
            count = 0
            dx_range = [-11, -10, -9, -1, 1, 9, 10, 11]

            if button_number <= 10:
                for i in [-10,-11,-9]:
                    if i in dx_range:
                        dx_range.remove(i)
            if button_number % 10 == 1:
                for i in [-1,-11,9]:
                    if i in dx_range:
                        dx_range.remove(i)
            if button_number % 10 == 0:
                for i in [1,11,-9]:
                    if i in dx_range:
                        dx_range.remove(i)
            if button_number >= 91:
                for i in [9,10,11]:
                    if i in dx_range:
                        dx_range.remove(i)


            for dx in dx_range:
                neighbor_number = button_number + dx
                if neighbor_number in self.random_numbers:
                    count += 1

            button.setText(str(count))
            self.set_button_color(button, QtGui.QColor("white"))
            self.open_count += 1
            self.titletextupdate()

        button.setStyleSheet("color: black")
        #print("Button clicked! Button Number:", button_number)

    def button_context_menu(self, position):
        button = self.sender()
        #color=self.get_button_color(button)
        if button.text() and button.text() != "#":
            return
        button_index = self.buttons.index(button)
        button_number = self.button_numbers[button_index]
        #button.setStyleSheet("color: black")

        if button.text() == '#':
            button.setText('')
            self.minecount += -1
            #self.set_button_color(button, QtGui.QColor("black"))

        else:
            button.setText('#')
            self.minecount += 1
            #self.set_button_color(button, QtGui.QColor("grey"))
        self.titletextupdate()
        #button.setStyleSheet("color: black")
        #print("Right-clicked! Set Button Number:", button_number)

    def set_button_color(self, button, color):
        palette = button.palette()
        palette.setColor(QtGui.QPalette.Button, color)
        button.setPalette(palette)

    def get_button_color(self, button):
        palette = button.palette()
        button_text_color = button_palette.color(QtGui.QPalette.ButtonText)
        return button_text_color
# 创建窗口实例
window = Minesweeper()
