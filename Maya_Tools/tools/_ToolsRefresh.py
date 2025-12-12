import os
import maya.cmds as cmds


def errerwindow(a,text):
    error_window = cmds.window(title="JCQrefresh", sizeable=True, resizeToFitChildren=True)
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label=text, backgroundColor=a, font="boldLabelFont", width=300, height=50)
    cmds.showWindow(error_window)

folder_path = r"S:\Public\qiu_yi\JCQ_Tool\codes"
py_folfer = folder_path+r"\tools"
icon_folfer =folder_path+r"\toolsicon"
doc_folfer =folder_path+r"\toolsdoc"
shelf_name = "JCQtool"
element_to_keep = "_JCQrefrash"

try:
    # 查询指定名称的shelfLayout是否存在
    shelf_exists = cmds.shelfLayout(shelf_name, query=True, exists=True)

    if shelf_exists:
        shelf_items = cmds.shelfLayout(shelf_name, query=True, childArray=True)

        if shelf_items:
            # 遍历shelfLayout中的子元素
            for item in shelf_items:
                item_name = cmds.shelfButton(item, query=True, label=True)

                # 检查元素名称是否匹配要保留的名称
                if item_name != element_to_keep:
                    # 删除不匹配的元素
                    cmds.deleteUI(item)
    else:
        cmds.shelfLayout(shelf_name, p="ShelfLayout")

    for file_name in os.listdir(py_folfer):
        if not file_name.endswith(".py"):
            continue  # 跳过非Python脚本文件
        if file_name == element_to_keep+".py":
            continue  # 跳过指定文件名
        # 获取Python脚本文件的完整路径
        script_path = os.path.join(py_folfer, file_name)

        # 获取对应的图标文件的完整路径
        icon_path = os.path.join(icon_folfer, file_name[:-3] + ".png")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(icon_folfer, "noimage.png")

        command = '''\
path = r"{0}"
exec(compile(open(path, 'rb').read(), path, 'exec'))'''.format(script_path)

        doc_path = os.path.join(doc_folfer, file_name[:-3] + ".png")
        if not os.path.exists(doc_path):
            doc_path = os.path.join(doc_folfer, "noimage.png")

        dc = '''\
import subprocess
subprocess.Popen(['start', r"{0}"], shell=True)'''.format(doc_path)

        button=cmds.shelfButton(
            command=command,
            image=icon_path,
            label=file_name[:-3],  # 移除文件扩展名作为按钮的标签
            parent=shelf_name,
            dcc=dc
        )
    errerwindow((1, 1, 1), "JCQ tool refrash success")
except:
    errerwindow((1, 0, 0),"JCQ tool refrash failied")



