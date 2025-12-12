import maya.cmds as cmds
import sys
# 获取 Maya 内置 Python 解释器的版本信息
maya_python_version = sys.version_info[:3]
# 判断版本并输出不同的字符串
if maya_python_version == (3, 7, 7):
    subsyspath ='S:\Public\qiu_yi\py3716\Lib\site-packages'
elif maya_python_version == (3, 10, 8):
    subsyspath ='S:\Public\qiu_yi\JCQ_Tool\Lib\site-packages'
elif maya_python_version == (3, 9, 7):
    subsyspath = 'S:\Public\qiu_yi\py397\Lib\site-packages'
sys.path.insert(0,subsyspath)
import io
import os.path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PIL import Image
import json

class JCQ_Reference_Tool():
    def __init__(self):
        with open('S:\Public\qiu_yi\JCQ_Tool\data\proptool_projectfile.json', 'r') as f:
            self.project_dir = json.load(f)
        self.project_List = None
        self.sheet_list = None
        self.imagesize_textField = None
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        self.SERVICE_ACCOUNT_FILE = 'S:/Public/qiu_yi/JCQ_Tool/data/project-gomapy-d737ea76a8ff.json'
        self.creds = service_account.Credentials.from_service_account_file(self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.projectname_list = list(self.project_dir.keys())
        self.default_Image_Path = 'S:/Public/qiu_yi/JCQ_Tool/data/images/'
        self.main_tabLayout = None

    def errerwindow(self,text):
        error_window = cmds.window(title="Error", sizeable=True, resizeToFitChildren=True)
        cmds.columnLayout(adjustableColumn=True)
        cmds.text(label=text, backgroundColor=(1, 0, 0), font="boldLabelFont", width=300, height=50)
        cmds.showWindow(error_window)

    def Create_Reference_tab(self,*args):

        def errerwindow(text):
            error_window = cmds.window(title="Error", sizeable=True, resizeToFitChildren=True)
            cmds.columnLayout(adjustableColumn=True)
            cmds.text(label=text, backgroundColor=(1, 0, 0), font="boldLabelFont", width=300, height=50)
            cmds.showWindow(error_window)

        def sheet_item(sheet_id, sheet, start_column, end_column, ignore_empty_or_length):
            range_string = f'{sheet}!{start_column}:{end_column}'
            result = self.service.spreadsheets().values().get(spreadsheetId=sheet_id, range=range_string).execute()
            values = result.get('values', [])
            list = []
            if not ignore_empty_or_length:
                if values:
                    for row in values:
                        if row:  # 忽略空行
                            list.append(row[0])
                return list
            else:
                if values:
                    for row in values:
                        if row:  # 忽略空行
                            list.append(row[0])
                        else:
                            list.append("")
                    if len(list) < ignore_empty_or_length:
                        for i in range(ignore_empty_or_length - len(list)):
                            list.append("")
                else:
                    list = [''] * ignore_empty_or_length
                return list

        def createsmallimage(image_path):
            if image_path and not image_path.endswith("\\"):
                try:
                    # 尝试打开第一个文件
                    original_image = Image.open(image_path)
                except FileNotFoundError:
                    # 如果第一个文件不存在，切换到第二个路径并打开文件
                    try:
                        original_image = Image.open(self.default_Image_Path+"noimage.png")
                    except FileNotFoundError:
                        # 如果两个路径都不存在文件，打印错误消息并退出程序
                        print("Error: image file not found!")
                        sys.exit(1)
            else:
                original_image = Image.open(self.default_Image_Path+"noimage.png")

            width, height = original_image.size
            i = width / height
            if i == 1:
                resized_image = original_image.resize((list_height, list_height))
                resized_image.save(self.default_Image_Path+"small.png")
            else:
                padded_image = Image.new('RGBA', (list_height, list_height), (0, 0, 0, 0))
                if i > 1:
                    resized_image = original_image.resize((list_height, int(list_height / i)))
                else:
                    resized_image = original_image.resize((int(list_height * i), list_height))
                padded_image.paste(resized_image, (0, 0))
                padded_image.save(self.default_Image_Path+"small.png")

            return self.default_Image_Path+"small.png"

        def Import_Reference_btn(namespace, path, file):
            full_path = path + '/' + file
            if namespace == '':
                namespace = ":"
            try:
                cmds.file(full_path,
                          reference=True,
                          type="mayaBinary",
                          ignoreVersion=True,
                          gl=True,
                          mergeNamespacesOnClash=False,
                          namespace=namespace,
                          options="v=0;")
            except:
                print("file read fail")
                pass

        def create_Tab(sheet_name):
            tab_names = cmds.tabLayout(self.main_tabLayout, query=True, childArray=True)

            def clear_layout(layout):
                children = cmds.layout(sheet_name + 'scrolllayout', q=True, childArray=True)
                if children:
                    for child in children:
                        cmds.deleteUI(child)
                clearlayoutcount = True

            if tab_names:
                if sheet_name + 'scrolllayout' in tab_names:
                    # cmds.tabLayout(self.main_tabLayout, edit=True, deleteTab=selected_item)
                    # cmds.deleteUI(selected_item+'scrolllayout',uiTemplate=True)
                    clear_layout(sheet_name + 'scrolllayout')
                    cmds.setParent(sheet_name + 'scrolllayout')
                    # return
                else:
                    scrollLayout = cmds.scrollLayout(
                        sheet_name + 'scrolllayout',
                        horizontalScrollBarThickness=16,
                        verticalScrollBarThickness=16,
                    )
                    cmds.tabLayout(self.main_tabLayout, edit=True, tp="west", tabLabel=((scrollLayout, sheet),))
                    cmds.setParent(sheet_name + 'scrolllayout')
            else:
                scrollLayout = cmds.scrollLayout(
                    sheet_name + 'scrolllayout',
                    horizontalScrollBarThickness=16,
                    verticalScrollBarThickness=16,
                )
                cmds.tabLayout(self.main_tabLayout, edit=True, tp="west", tabLabel=((scrollLayout, sheet),))
                cmds.setParent(sheet_name + 'scrolllayout')

        list_height = int(cmds.textFieldGrp(self.imagesize_textField, query=True, text=True))
        try:
            num = int(list_height)
            if 0 < num <= 500:
                list_height = num
            else:
                errerwindow("size too big or too small,should be between 1and500")
                return
        except ValueError:
            errerwindow("ValueError,should be between 1and500")
            return

        project = cmds.optionMenu(self.project_List, query=True, value=True)
        sheet = cmds.optionMenu(self.sheet_list, query=True, value=True)

        sheetId = self.project_dir[project]

        Name_ls = sheet_item(sheetId, sheet, "A2", "A", 0)
        Namespace_ls = sheet_item(sheetId, sheet, "B2", "B", len(Name_ls))
        image_path_ls = sheet_item(sheetId, sheet, "D2", "D", len(Name_ls))
        image_name_ls = sheet_item(sheetId, sheet, "E2", "E", len(Name_ls))
        flie_path_ls = sheet_item(sheetId, sheet, "F2", "F", len(Name_ls))
        file_name_ls = sheet_item(sheetId, sheet, "G2", "G", len(Name_ls))

        # print(Namespace_ls)

        cmds.setParent(self.main_tabLayout)
        create_Tab(sheet)

        # 创建
        if Name_ls:
            Name_lsmax_len = max(len(max(Name_ls, key=len)) * 9+20, 20)
            Namespace_lsmax_len = max(len(max(Namespace_ls, key=len)) * 9+20, 20)
            x=1
            for i in range(len(Name_ls)):
                cmds.rowLayout(numberOfColumns=4, columnWidth4=(Name_lsmax_len, Namespace_lsmax_len, list_height + 20, 100), adjustableColumn=4,
                               columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0), (4, 'both', 0)])
                n = i
                cmds.text(label=str(x)+". "+Name_ls[n])
                cmds.text(label=Namespace_ls[n])
                cmds.picture(image=createsmallimage(image_path_ls[n] + "\\" + image_name_ls[n]), height=list_height)
                # print(image_path_ls[n]+ "/" + image_name_ls[n])
                button = cmds.button(Namespace_ls[n] + "button", label="Import Reference",
                                     command=lambda x, namespace=Namespace_ls[n], path=flie_path_ls[n],
                                                    file=file_name_ls[n]: Import_Reference_btn(
                                         namespace, path, file))
                cmds.setParent('..')
                x=x+1
        cmds.tabLayout(self.main_tabLayout, edit=True, selectTab=sheet + 'scrolllayout')

    def create_Window(self):

        def open_ReferenceEditor(*args):
            cmds.ReferenceEditor()

        def change_prop_list(selection):
            sheetId = self.project_dir[selection]
            sheet_metadata = self.service.spreadsheets().get(spreadsheetId=sheetId).execute()
            sheets = sheet_metadata.get('sheets', [])
            all_sheet_names = [sheet.get('properties', {}).get('title', 'Sheet1') for sheet in sheets]
            cmds.optionMenu(self.sheet_list, edit=True, deleteAllItems=True)
            for project_name in all_sheet_names:
                cmds.menuItem(label=project_name, parent=self.sheet_list)

        # 创建主窗口
        JCQ_RT_N = "JCQ_Reference_Tool"
        JCQ_RT_T = "JCQ Reference Tool"
        size = (450, 400)
        # 检查是否存在窗口
        if cmds.window(JCQ_RT_N, exists=True):
            cmds.deleteUI(JCQ_RT_N, window=True)

        window = cmds.window(JCQ_RT_N, title=JCQ_RT_T, widthHeight=size)
        Reference_Tool_Form = cmds.formLayout(numberOfDivisions=100)

        # 创建下拉列表1
        self.project_List = cmds.optionMenu(label='select project', width=200, changeCommand=change_prop_list)
        for project_name in self.projectname_list:
            cmds.menuItem(label=project_name, parent=self.project_List)
        selected = cmds.optionMenu(self.project_List, query=True, value=True)

        # 创建下拉列表2
        self.sheet_list = cmds.optionMenu(label='select list', width=200)
        change_prop_list(selected)

        self.imagesize_textField = cmds.textFieldGrp("image size", label="image size", text=100, columnAlign=(1, "left"), columnWidth2=(92, 100))
        Reference_Tool_Createtab_Button = cmds.button(label='Create tab', width=200, command=self.Create_Reference_tab)
        ReferenceED_Button = cmds.button(label='open Reference Editor', width=200, command=open_ReferenceEditor)

        self.main_tabLayout = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
        cmds.formLayout(Reference_Tool_Form, edit=True,
                        attachForm=[
                            (self.project_List, 'top', 5),
                            (self.sheet_list, 'top', 5),
                            (self.imagesize_textField, 'left', 5),
                            (ReferenceED_Button, 'left', 5),
                            (self.main_tabLayout, 'left', 5),
                            (self.main_tabLayout, 'bottom', 5),
                            (self.main_tabLayout, 'right', 5),
                        ],
                        attachControl=[
                            (self.imagesize_textField, 'top', 5, self.project_List),
                            (Reference_Tool_Createtab_Button, 'top', 5, self.project_List),
                            (ReferenceED_Button, 'top', 5, self.imagesize_textField),
                            (self.main_tabLayout, 'top', 5, ReferenceED_Button),
                            (self.sheet_list, 'left', 5, self.project_List),
                            (Reference_Tool_Createtab_Button, 'left', 5, self.imagesize_textField),
                        ])

        # 显示主窗口
        cmds.showWindow(window)

JCQ_BSimageViewer_GUI  = JCQ_Reference_Tool()
JCQ_BSimageViewer_GUI.create_Window()