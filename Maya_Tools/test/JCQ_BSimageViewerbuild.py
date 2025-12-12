import maya.cmds as cmds
import sys

maya_python_version = sys.version_info[:3]
if maya_python_version == (3, 7, 7):
    subsyspath = 'S:\Public\qiu_yi\py3716\Lib\site-packages'
elif maya_python_version == (3, 10, 8):
    subsyspath = 'S:\Public\qiu_yi\JCQ_Tool\Lib\site-packages'
elif maya_python_version == (3, 9, 7):
    subsyspath = 'S:\Public\qiu_yi\py397\Lib\site-packages'
sys.path.insert(0, subsyspath)
import io
import os.path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PIL import Image
import json


class JCQ_BS_image_Viewer():

    def __init__(self):
        with open('S:\Public\qiu_yi\JCQ_Tool\data\BScloudfile.json', 'r') as f:
            self.BSIV_data = json.load(f)
            self.project_list = list(self.BSIV_data.keys())
        self.size_textField = None
        self.main_tabs = None
        self.checkBox_selectBS = None
        self.checkBox_use_namespace = None
        self.sheet_list = None
        self.project_option_menu = None
        self.default_Image_Path = 'S:\\Public\\qiu_yi\\JCQ_Tool\\data\\images\\'

    def errerwindow(self, text):
        error_window = cmds.window("error window", title="error", widthHeight=(400, 200))
        cmds.columnLayout(adjustableColumn=True)
        cmds.text(label=text)
        cmds.showWindow(error_window)

    def get_project_sheetlist(self, spreadsheet_id):
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        SERVICE_ACCOUNT_FILE = 'S:/Public/qiu_yi/JCQ_Tool/data/project-gomapy-d737ea76a8ff.json'

        # 创建服务帐号凭据
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        # 创建 Sheets API 客户端
        service = build('sheets', 'v4', credentials=creds)

        # 获取所有 sheet 的名称
        sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', [])
        sheet_names = [sheet.get('properties', {}).get('title', 'Sheet1') for sheet in sheets]
        return sheet_names

    def create_labels(self, *args):
        selected_project = cmds.optionMenu(self.project_option_menu, query=True, value=True)
        spreadsheet_id = self.BSIV_data[selected_project]

        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        SERVICE_ACCOUNT_FILE = 'S:/Public/qiu_yi/JCQ_Tool/data/project-gomapy-d737ea76a8ff.json'

        # 创建服务帐号凭据
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        # 创建 Sheets API 客户端
        service = build('sheets', 'v4', credentials=creds)

        # 获取所有 sheet 的名称
        sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', [])
        sheet_names = [sheet.get('properties', {}).get('title', 'Sheet1') for sheet in sheets]

        list_height = cmds.textFieldGrp(self.size_textField, query=True, text=True)

        try:
            num = int(list_height)
            if 0 < num <= 500:
                list_height = num
            else:
                self.errerwindow("too big or too small")
                return
                list_height = 100
        except ValueError:
            self.errerwindow("ValueError")
            return
            list_height = 100

        def clear_layout(layout):
            children = cmds.layout(selected_item + 'scrolllayout', q=True, childArray=True)
            if children:
                for child in children:
                    cmds.deleteUI(child)
            clearlayoutcount = True

        # 获取选中的sheet名称
        selected_item = cmds.optionMenu(self.sheet_list, query=True, value=True)
        matching_items = [name for name in sheet_names if name == selected_item]

        def get_spreadsheet_values_single(service, spreadsheet_id, range_name):
            result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
            item = result.get('values', [])
            try:

                values = item[0][0]
            except:
                values = None
            # print(values)
            return values

        def get_spreadsheet_values_list(service, spreadsheet_id, range_name):
            result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
            values = result.get('values', [])
            list = []
            if values:
                for row in values:
                    if row:  # 忽略空行
                        list.append(row[0])
            return list

        if matching_items:

            parent = get_spreadsheet_values_single(service, spreadsheet_id, f'{selected_item}!F2')
            if parent:
                ShapesNames = get_spreadsheet_values_list(service, spreadsheet_id, f'{parent}!A3:A')
            else:
                ShapesNames = get_spreadsheet_values_list(service, spreadsheet_id, f'{selected_item}!A3:A')
            BlendShapeName = get_spreadsheet_values_single(service, spreadsheet_id, f'{selected_item}!A2')
            Namespace = get_spreadsheet_values_single(service, spreadsheet_id, f'{selected_item}!B2')
            image_path = get_spreadsheet_values_single(service, spreadsheet_id, f'{selected_item}!C2')
            imageType = get_spreadsheet_values_single(service, spreadsheet_id, f'{selected_item}!D2')
            if cmds.checkBox(self.checkBox_use_namespace, q=True, value=True) == True:
                BSName = Namespace + ":" + BlendShapeName
            else :
                BSName = BlendShapeName


            def slider_dragged(item, value):
                BSNUM = 0
                for i in range(len(ShapesNames)):
                    if ShapesNames[i] == item:
                        BSNUM = i
                try:
                    cmds.setAttr(BSName + "." + item, value)
                    # cmds.blendShape(BSName, edit=True, w=[(BSNUM, value)])
                    cmds.textFieldGrp(BSName + item + "textFieldGrp", edit=True, text="{:.3f}".format(value))
                except:
                    pass

            def textFieldchange(item, text):
                try:
                    float(text)
                except:
                    return
                try:
                    cmds.setAttr(BSName + "." + item, float(text))
                    # cmds.blendShape(BSName, edit=True, w=[(BSNUM, value)])
                    cmds.floatSliderGrp(BSName + item + "slider", edit=True, value=float(text))
                except:
                    pass

            def btnsetkey(label, BSName, item):
                # print("press success")

                current_time = cmds.currentTime(query=True)
                key_count = cmds.keyframe(BSName + "." + item, time=(current_time, current_time), query=True, keyframeCount=True)
                data_now = cmds.getAttr(BSName + "." + item)

                if key_count >= 1:
                    key_now = cmds.keyframe(BSName + "." + item, query=True, time=(current_time, current_time), valueChange=True)
                    # print(key_now[0])
                    # print(data_now)
                    if key_now[0] == data_now:
                        cmds.cutKey(BSName + "." + item, time=(current_time, current_time))
                        # print("key delete")
                    else:
                        cmds.setKeyframe(BSName + "." + item, v=data_now)
                        # print("key reset")

                else:
                    cmds.setKeyframe(BSName + "." + item, v=data_now)
                    # print("key")
                try:
                    current_time = cmds.currentTime(query=True)
                    key_count = cmds.keyframe(BSName + "." + item, time=(current_time, current_time), query=True, keyframeCount=True)
                    if key_count == 1:
                        cmds.button(BSName + item + "button", edit=True, backgroundColor=[1, 0, 0])
                        # print("botton red")

                    else:
                        if cmds.keyframe(BSName + "." + item, query=True, keyframeCount=True) > 0:
                            cmds.button(BSName + item + "button", edit=True, backgroundColor=[1, 0.5, 0.5])
                            # print("botton pink")

                        else:
                            cmds.button(BSName + item + "button", edit=True, backgroundColor=[0.45, 0.45, 0.45])
                            # print("botton grey")

                except:
                    pass
                if cmds.checkBox(self.checkBox_selectBS, q=True, value=True) == True:
                    cmds.select(BSName)

            def createsmallimage(image_path, item, imageType):
                try:
                    # 尝试打开第一个文件
                    original_image = Image.open(image_path + "\\" + item + "." + imageType)
                except FileNotFoundError:
                    # 如果第一个文件不存在，切换到第二个路径并打开文件
                    try:
                        print("Error: " + image_path + "\\" + item + "." + imageType + " not found!")
                        original_image = Image.open(self.default_Image_Path + "noimage.png")
                    except FileNotFoundError:
                        # 如果两个路径都不存在文件，打印错误消息并退出程序
                        print("Error: image file not found!")
                        sys.exit(1)
                resized_image = original_image.resize((list_height, list_height))
                resized_image.save(self.default_Image_Path + "small.png")
                return self.default_Image_Path + "small.png"

            def update_data(BSName, ShapesNames):
                for item in ShapesNames:
                    data_now = cmds.getAttr(BSName + "." + item)
                    cmds.floatSliderGrp(BSName +item + "slider", edit=True, value=float("{:.3f}".format(cmds.getAttr(data_now))))
                    cmds.textFieldGrp(BSName +item + "textFieldGrp", edit=True, text=float("{:.3f}".format(cmds.getAttr(data_now))))
                    current_time = cmds.currentTime(query=True)
                    key_count = cmds.keyframe(BSName + "." + item, time=(current_time, current_time), query=True, keyframeCount=True)
                    if key_count == 1:
                        cmds.button(item + "button", edit=True, backgroundColor=[1, 0, 0])
                    else:
                        if cmds.keyframe(BSName + "." + item, query=True, keyframeCount=True) > 0:
                            cmds.button(item + "button", edit=True, backgroundColor=[1, 0.5, 0.5])
                        else:
                            cmds.button(item + "button", edit=True, backgroundColor=[0.45, 0.45, 0.45])

            def update_data_v2(BSName, item):
                def attribute_changed_callback(BSName, item, *args, ):
                    attribute_value = cmds.getAttr(BSName + "." + item)
                    current_time = cmds.currentTime(query=True)
                    key_count = cmds.keyframe(BSName + "." + item, time=(current_time, current_time), query=True, keyframeCount=True)
                    data_now = cmds.getAttr(BSName + "." + item)

                    cmds.floatSliderGrp(BSName +item + "slider", edit=True, value=float("{:.3f}".format(data_now)))
                    cmds.textFieldGrp(BSName +item + "textFieldGrp", edit=True, text=float("{:.3f}".format(data_now)))

                    if key_count >= 1:
                        key_now = cmds.keyframe(BSName + "." + item, query=True, time=(current_time, current_time), valueChange=True)
                        # print(data_now)
                        # print(key_now)
                        if key_now[0] == data_now:
                            cmds.button(BSName +item + "button", edit=True, backgroundColor=[1, 0, 0])
                        else:
                            cmds.button(BSName +item + "button", edit=True, backgroundColor=[1, 0.5, 0.5])


                    else:
                        if cmds.keyframe(BSName + "." + item, query=True, keyframeCount=True) > 0:
                            cmds.button(BSName +item + "button", edit=True, backgroundColor=[1, 0.5, 0.5])

                        else:
                            cmds.button(BSName +item + "button", edit=True, backgroundColor=[0.45, 0.45, 0.45])

                cmds.scriptJob(attributeChange=[BSName + "." + item, lambda BSName=BSName, item=item: attribute_changed_callback(BSName, item)])
                cmds.scriptJob(ct=["UndoAvailable", lambda BSName=BSName, item=item: attribute_changed_callback(BSName, item)])
                cmds.scriptJob(event=["timeChanged", lambda BSName=BSName, item=item: attribute_changed_callback(BSName, item)])

            # 创建新窗口
            cmds.setParent(self.main_tabs)
            tab_names = cmds.tabLayout(self.main_tabs, query=True, childArray=True)

            if tab_names:
                if selected_item + 'scrolllayout' in tab_names:
                    # cmds.tabLayout(self.main_tabs, edit=True, deleteTab=selected_item)
                    # cmds.deleteUI(selected_item+'scrolllayout',uiTemplate=True)
                    clear_layout(selected_item + 'scrolllayout')
                    cmds.setParent(selected_item + 'scrolllayout')
                    # return
                else:
                    scrollLayout = cmds.scrollLayout(
                        selected_item + 'scrolllayout',
                        horizontalScrollBarThickness=16,
                        verticalScrollBarThickness=16,
                    )
                    cmds.tabLayout(self.main_tabs, edit=True, tp="west", tabLabel=((scrollLayout, selected_item),))
                    cmds.setParent(selected_item + 'scrolllayout')
            else:
                scrollLayout = cmds.scrollLayout(
                    selected_item + 'scrolllayout',
                    horizontalScrollBarThickness=16,
                    verticalScrollBarThickness=16,
                )
                cmds.tabLayout(self.main_tabs, edit=True, tp="west", tabLabel=((scrollLayout, selected_item),))
                cmds.setParent(selected_item + 'scrolllayout')
            # 创建标签和控制器
            if not cmds.objExists(BSName):
                self.errerwindow(BSName + "dont exist")
                return

            for item in ShapesNames:
                cmds.rowLayout(numberOfColumns=6, columnWidth6=(150, list_height, list_height, 150, 50, 50))
                if cmds.objExists(BSName + "." + item):
                    cmds.text(label=item)
                    cmds.picture(image=createsmallimage(image_path, "default", imageType), height=list_height)
                    cmds.picture(image=createsmallimage(image_path, item, imageType), height=list_height)
                    try:
                        slider_value = float("{:.3f}".format(cmds.getAttr(BSName + "." + item)))
                    except:
                        slider_value = 0.00
                    slider = cmds.floatSliderGrp(BSName + item + "slider", minValue=.0, maxValue=1.0,
                                                 value=slider_value, precision=3, field=True,
                                                 columnAlign=(1, "left"), columnWidth2=(0, 150),
                                                 dragCommand=lambda value, x=item: slider_dragged(x, value))
                    # print(item+"textFieldGrp")
                    textField = cmds.textFieldGrp(BSName + item + "textFieldGrp", label=item + "textFieldGrp",
                                                  text=slider_value, columnAlign=(1, "left"), columnWidth2=(0, 40),
                                                  textChangedCommand=lambda text, x=item: textFieldchange(x, text))
                    button = cmds.button(BSName + item + "button", label="key",
                                         command=lambda label, BSName=BSName, item=item: btnsetkey(label, BSName, item))
                    update_data_v2(BSName, item)
                    cmds.setParent('..')
                else:
                    cmds.text(label=item+" dont exist",height=list_height)
                    cmds.setParent('..')
            try:
                update_data(BSName, ShapesNames)
            except:
                pass

            cmds.tabLayout(self.main_tabs, edit=True, selectTab=selected_item + 'scrolllayout')

    def create_Window(self):
        def update_sheet_list():
            selected_project = cmds.optionMenu(self.sheet_list, query=True, value=True)
            menu_list = get_project_sheetlist(selected_project)
            for project_name in menu_list:
                cmds.menuItem(label=project_name)

        def open_ShapeEditor(self, *args):
            cmds.ShapeEditor()

        def open_GraphEditor(self, *args):
            cmds.GraphEditor()

        # 创建主窗口
        JCQ_MAYABS_MW_N = "JCQ_BSi_MainWindow"
        JCQ_MAYABS_MW_T = "JCQ_BS image Viewer"
        size = (600, 400)
        # 检查是否存在窗口
        if cmds.window(JCQ_MAYABS_MW_N, exists=True):
            cmds.deleteUI(JCQ_MAYABS_MW_N, window=True)
        # 删除旧job
        job_list = cmds.scriptJob(listJobs=True)
        job_delete_list = []
        for job in job_list:
            if "JCQ_BS_image_Viewer" in job:
                job_delete_list.append(job)
        NUM_list = [item.split(':')[0].strip() for item in job_delete_list]
        for i in NUM_list:
            cmds.scriptJob(kill=int(i))

        # 创建新窗口
        window = cmds.window(JCQ_MAYABS_MW_N, title=JCQ_MAYABS_MW_T, widthHeight=size)
        Main_Form = cmds.formLayout(numberOfDivisions=100)
        # 创建下拉列表1
        self.project_option_menu = cmds.optionMenu(label='select project', width=200)
        for project_name in self.project_list:
            cmds.menuItem(label=project_name, command=update_sheet_list)
        # 创建下拉列表2
        selected_project = cmds.optionMenu(self.project_option_menu, query=True, value=True)
        target_list = self.get_project_sheetlist(self.BSIV_data[selected_project])
        self.sheet_list = cmds.optionMenu(label='select list', width=200)
        for target in target_list:
            cmds.menuItem(label=target, command=self.create_labels)

        self.checkBox_selectBS = cmds.checkBox(label='key and select BS', v=True)
        self.checkBox_use_namespace = cmds.checkBox(label='use namespace', v=True)
        # 创建按钮并绑定函数
        Create_Button = cmds.button(label='create tab', width=300, command=self.create_labels)
        ShapeEditor_Button = cmds.button(label='open ShapeEditor', width=150, command=open_ShapeEditor)
        GraphEditor_Button = cmds.button(label='open GraphEditor', width=150, command=open_GraphEditor)

        self.size_textField = cmds.textFieldGrp(label="Example Image size", text=100, columnAlign=(1, "left"), columnWidth2=(112, 80))

        self.main_tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)


        cmds.formLayout(Main_Form, edit=True,
                        attachForm=[
                            (self.project_option_menu, 'top', 5),
                            (self.sheet_list, 'top', 5),
                            (self.project_option_menu, 'left', 5),
                            (self.size_textField, 'left', 5),
                            (self.main_tabs, 'left', 5),
                            (self.main_tabs, 'bottom', 5),
                            (self.main_tabs, 'right', 5),
                            (ShapeEditor_Button, 'left', 5)
                        ],
                        attachControl=[

                            (self.sheet_list, 'left', 5, self.project_option_menu),
                            (Create_Button, 'top', 5, self.project_option_menu),
                            (self.size_textField, 'top', 5, self.project_option_menu),
                            (ShapeEditor_Button, 'top', 5, Create_Button),
                            (self.checkBox_selectBS, 'top', 5, Create_Button),
                            (self.checkBox_use_namespace, 'top', 5, Create_Button),
                            (GraphEditor_Button, 'top', 5, Create_Button),
                            (self.main_tabs, 'top', 5, ShapeEditor_Button),
                            (Create_Button, 'left', 5, self.size_textField),
                            (self.checkBox_selectBS, 'left', 5, GraphEditor_Button),
                            (self.checkBox_use_namespace, 'left', 5, self.checkBox_selectBS),
                            (GraphEditor_Button, 'left', 5, ShapeEditor_Button)
                        ])

        # 显示主窗口
        cmds.showWindow(window)


JCQ_BSimageViewer = JCQ_BS_image_Viewer()
JCQ_BSimageViewer.create_Window()