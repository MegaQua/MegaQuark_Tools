import maya.cmds as cmds
import sys

maya_python_version = sys.version_info[:3]
if maya_python_version == (3, 7, 7):
    subsyspath = 'S:\Public\qiu_yi\py3716\Lib\site-packages'
elif maya_python_version == (3, 10, 8):
    subsyspath = 'S:\Public\qiu_yi\JCQ_Tool\Lib\site-packages'
elif maya_python_version == (3, 9, 7):
    subsyspath = 'S:\Public\qiu_yi\py397\Lib\site-packages'
else:
    subsyspath = 'S:\Public\qiu_yi\py3716\Lib\site-packages'

sys.path.insert(0, subsyspath)
import io
import os.path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PIL import Image
import json
from PySide2 import QtWidgets, QtGui, QtCore
import requests
import random
import string
import json
class MyWindow(QtWidgets.QWidget):
    def __init__(self):
        super(MyWindow, self).__init__(None)

        self.setWindowTitle("random cat")

        # 创建QLabel控件
        label = QtWidgets.QLabel("Click Me", self)

        # 加载并显示随机GIF图像
        gif_url = self.get_random_gif_url()
        #print(gif_url)
        filename = "S:\Public\qiu_yi\JCQ_Tool\data\images\cat.gif"
        response = requests.get(gif_url)
        response.raise_for_status()
        with open(filename, "wb") as file:
            file.write(response.content)
        movie = QtGui.QMovie()
        movie.setCacheMode(QtGui.QMovie.CacheAll)
        movie.setFileName("S:\Public\qiu_yi\JCQ_Tool\data\images\cat.gif")
        label.setMovie(movie)
        movie.start()

        # 创建布局
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

        # 显示窗口
        self.show()

    def get_random_gif_url(self):
        # set the apikey and limit
        apikey = "AIzaSyBOwuqeq97Tre4MrUEccx7nQWTOq12fT4E"  # click to set to your apikey
        lmt = 8
        ckey = "randomgif"  # set the client_key for the integration and use the same value for all API calls

        # our test search
        keywordlist = ["flying cat","running cat","jumpping cat","many cat","cat bread","tigger cat","cat fail","meow","cat","Tom and Jerry","cat meme","cat girl","fighting cat","meme cat","fat cat",'fluffy cat', 'sleek cat', 'cute cat', 'mischievous cat', 'graceful cat', 'curious cat', 'sleepy cat', 'friendly cat', 'fierce cat', 'adorable cat', 'kitty', 'chubby cat']
        random_keywords = []

        random_keyword = ''.join(random.choices(string.ascii_lowercase, k=10))  # 生成随机关键词
        #search_term = random.choice(keywordlist)
        search_term = random.choice(keywordlist)+" "+random_keyword
        # get the top 8 GIFs for the search term
        r = requests.get(
            "https://tenor.googleapis.com/v2/search?q=%s&key=%s&client_key=%s&limit=%s" % (search_term, apikey, ckey, lmt))

        if r.status_code == 200:
            # load the GIFs using the urls for the smaller GIF sizes
            top_8gifs = json.loads(r.content)
            #print(top_8gifs)
            # 获取results列表
            results = top_8gifs['results']

            # 从results中随机选择一个字典
            random_result = random.choice(results)

            # 获取该字典中的gif链接
            gif_url = random_result['media_formats']['gif']['url']
            return gif_url
        else:
            top_8gifs = "S:/Public/qiu_yi/JCQ_Tool/data/images/cat.gif"


# 创建并自动显示窗口实例
window = MyWindow()
