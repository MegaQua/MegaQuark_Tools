import os
import requests
import feedparser
from datetime import datetime
import pyautogui
import pyperclip
import time
import subprocess
import pytz

RSS_url="https://rsshub.app/twitter/user/ArknightsStaff"
feed = feedparser.parse(RSS_url)