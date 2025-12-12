# -*- coding: utf-8 -*-
try:
    from PySide2 import QtWidgets, QtCore, QtWebEngineWidgets
except Exception:
    from PySide6 import QtWidgets, QtCore, QtWebEngineWidgets

import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

url = "https://media1.tenor.com/m/x8v1oNUOmg4AAAAd/rickroll-roll.gif"

maya_main = wrapInstance(int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)

win = QtWidgets.QDialog(maya_main)
win.setWindowTitle("give you up")
win.setFixedSize(320, 320)

layout = QtWidgets.QVBoxLayout(win)
view = QtWebEngineWidgets.QWebEngineView()
view.setUrl(url)
layout.addWidget(view)

win.show()
