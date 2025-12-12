import sys
sys.path.insert(0, '/Lib/site-packages')

import io
import os.path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from PIL import Image

import json
with open('/data/BScloudfile.json', 'r') as f:
    data = json.load(f)
    omoide_facial_id = data['cloudid']['omoide_facial']



SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = '/data/project-gomapy-d737ea76a8ff.json'

# 创建服务帐号凭据
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# 创建 Sheets API 客户端
service = build('sheets', 'v4', credentials=creds)

# 设置要读取的单元格范围
spreadsheet_id = omoide_facial_id
# 获取所有 sheet 的名称
sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
sheets = sheet_metadata.get('sheets', [])
sheet_names = [sheet.get('properties', {}).get('title', 'Sheet1') for sheet in sheets]

import maya.cmds as cmds

def create_labels(*args):
    # 获取选中的sheet名称
    selected_item = cmds.optionMenu(option_menu, query=True, value=True)
    matching_items = [name for name in sheet_names if name == selected_item]

    if matching_items:
        # 创建新窗口
        new_window = cmds.window(title="标签窗口", widthHeight=(600, 400))
        cmds.columnLayout(adjustableColumn=True)

        range_name = f'{selected_item}!C2:C'
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get('values', [])

        # 将 A 列中的数据存储到列表中
        column_a_values = []
        if values:
            for row in values:
                if row:  # 忽略空行
                    column_a_values.append(row[0])

        # 创建标签和控制器
        for item in column_a_values:
            cmds.rowLayout(numberOfColumns=4, columnWidth4=[100, 150, 100, 150], columnAlign4=['left', 'left', 'left', 'left'])
            cmds.text(label=item, align='left', width=100)



            original_image = Image.open(r'/data/images/noimage.png')
            resized_image = original_image.resize((50, 50))
            resized_image.save(r'S:\Public\qiu_yi\JCQ_Tool\data\images\small.png')

            cmds.picture(image=r'S:\Public\qiu_yi\JCQ_Tool\data\images\small.png', width=150, height=100)
            slider_value = cmds.floatSlider(minValue=0, maxValue=1, value=0, width=100)
            text_value = cmds.textFieldButtonGrp(label='Value:', text='5', buttonLabel='Print', buttonCommand=lambda x: print(slider_value))
            cmds.setParent('..')

        # 显示新窗口
        cmds.showWindow(new_window)

# 创建主窗口
JCQ_MAYABS_MW_N = "JCQ_MAYABS_MainWindow"
JCQ_MAYABS_MW_T = "JCQ_MAYABS_MainWindow"
size = (400, 100)
# 检查是否存在窗口
if cmds.window(JCQ_MAYABS_MW_N, exists=True):
    cmds.deleteUI(JCQ_MAYABS_MW_N,window=True)

# 创建新窗口

window = cmds.window(JCQ_MAYABS_MW_N,title=JCQ_MAYABS_MW_T, widthHeight=size)
cmds.columnLayout(adjustableColumn=True)

# 创建下拉列表
option_menu = cmds.optionMenu(label='选项列表', width=300)
for sheet_name in sheet_names:
    cmds.menuItem(label=sheet_name)

# 创建按钮并绑定函数
cmds.button(label='创建标签', width=300, command=create_labels)

# 显示主窗口
cmds.showWindow(window)