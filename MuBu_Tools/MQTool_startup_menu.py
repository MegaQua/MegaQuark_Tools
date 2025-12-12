# -*- coding: utf-8 -*-
import os
import random
from pyfbsdk import FBMenuManager, FBApplication, FBConfigFile

TOOLS = {}

def get_tools_dir():
    cfg = FBConfigFile("@Application.txt")
    d = cfg.Get("Python", "PythonStartup")
    if not d:
        return None
    d = os.path.join(os.path.dirname(d), "Scripts", "tools")
    os.makedirs(d, exist_ok=True)
    return d

def eventMenu(ctrl, evt):
    s = TOOLS.get(evt.Id)
    if s and os.path.exists(s):
        FBApplication().ExecuteScript(s)

def load_tools(menu):
    d = get_tools_dir()
    if not d:
        return
    menu.OnMenuActivate.Add(eventMenu)
    for f in os.listdir(d):
        if f.lower().endswith(".py"):
            p = os.path.join(d, f).replace("\\", "/")
            i = random.randint(1000, 9999)
            TOOLS[i] = p
            menu.InsertLast(f, i)

def main():
    name = "MQTool"
    mgr = FBMenuManager()
    if mgr.GetMenu(name):
        return
    mgr.InsertBefore(None, "Help", name)
    menu = mgr.GetMenu(name)
    if not menu:
        return
    load_tools(menu)

main()
