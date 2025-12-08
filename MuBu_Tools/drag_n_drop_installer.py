# -*- coding: utf-8 -*-
import os
import shutil
from pyfbsdk import FBSystem, FBMessageBox, FBApplication

CUR = os.path.dirname(os.path.abspath(__file__))

def mb_ver_folder():
    v = str(int(FBSystem().Version))[:2]
    return "20" + v

def main():
    tool_src = os.path.join(CUR, "tools")
    startup_src = os.path.join(CUR, "JCQtool_startup_menu.py")

    if not os.path.isdir(tool_src):
        FBMessageBox("Error", tool_src, "OK")
        return
    if not os.path.isfile(startup_src):
        FBMessageBox("Error", startup_src, "OK")
        return

    ver = mb_ver_folder()
    home = os.path.expanduser("~")
    root = os.path.join(home, "Documents", "MB", ver)
    if not os.path.isdir(root):
        FBMessageBox("Error", root, "OK")
        return

    cfg = os.path.join(root, "config")
    scripts = os.path.join(cfg, "Scripts")
    startup = os.path.join(cfg, "PythonStartup")
    dst_tools = os.path.join(scripts, "tools")

    os.makedirs(scripts, exist_ok=True)
    os.makedirs(startup, exist_ok=True)

    if os.path.isdir(dst_tools):
        shutil.rmtree(dst_tools)
    shutil.copytree(tool_src, dst_tools)

    dst_startup = os.path.join(startup, "JCQtool_startup_menu.py")
    shutil.copy2(startup_src, dst_startup)

    FBApplication().ExecuteScript(dst_startup)
    FBMessageBox("Done", ver, "OK")

if __name__ in ("builtins", "__main__"):
    main()
