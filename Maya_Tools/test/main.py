import sys
sys.path.insert(0, '/Lib/site-packages')
import uritemplate
from google.oauth2 import service_account
from googleapiclient.discovery import build


SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# 创建服务帐号凭据
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# 创建 Sheets API 客户端
service = build('sheets', 'v4', credentials=creds)

# 设置要读取的单元格范围
spreadsheet_id = '1EEDH8wTujgfEswmazzXcddCK_1k3m7ervTTASwcra_E'
range_name = 'Chara_Prop_List!C3'

# 通过 Sheets API 获取单元格数据
result = service.spreadsheets().values().get(
    spreadsheetId=spreadsheet_id, range=range_name).execute()

def get_spreadsheet_values_single(service, spreadsheet_id, range_name):
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    item = result.get('values', [])
    values = item[0][0]
    print(values)
    return values

get_spreadsheet_values(service, spreadsheet_id, range_name)

"""# 打印获取的值
values = result.get('values', [])
if not values:
    print('No data found.')
else:
    for row in values:
        print(row)"""
