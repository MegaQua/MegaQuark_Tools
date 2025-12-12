import os
import platform
import re
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Google Sheets 配置
SPREADSHEET_ID = '1MoPoarQkDNVdOHGfmO0Ong7fyZCrAynARCKHyYDhkEc'
RANGE_NAME = 'Sheet1'
SERVICE_ACCOUNT_FILE = 'S:/Public/qiu_yi/JCQ_Tool/data/project-gomapy-d737ea76a8ff.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# 固定字段顺序
COLUMN_ORDER = [
    "PC Name",
    "OS Version",
    "Product Name",
    "Product ID",
    "Installed Key",
    "Original Key",
    "OEM Key",
    "Original Edition"
]

# 判断是否为 Windows 11
def get_windows_version(version_string: str = None):
    def extract_major_version(v_str):
        match = re.match(r"(\d+)", v_str)
        if match:
            return int(match.group(1))
        return 0

    if version_string:
        major_version = extract_major_version(version_string)
    else:
        try:
            version_parts = platform.version().split('.')
            major_version = int(version_parts[0]) if version_parts else 0
        except:
            major_version = 0

    if major_version >= 22000:
        return "Windows 11"
    elif major_version > 0:
        return "Windows 10"
    else:
        return "Unknown"

# 解析单个TXT文件为字典
def parse_txt_file(file_path):
    data = {}
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            match = re.match(r'^([^:]+):\s*(.+)$', line.strip())
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                data[key] = value
    return data

# 上传数据到 Google 表格
def upload_to_sheet(data_list: list):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    # 检查是否已有内容
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    rows = result.get('values', [])

    # 如果是空表，写入标题行
    if not rows:
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': [COLUMN_ORDER]}
        ).execute()

    # 写入每一行数据（按指定顺序）
    for data in data_list:
        row = [data.get(col, '') for col in COLUMN_ORDER]
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': [row]}
        ).execute()

# 主函数：遍历文件夹上传所有TXT
def main(folder_path):
    all_data = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            parsed = parse_txt_file(file_path)

            row_data = {
                "PC Name": filename,
                "OS Version": get_windows_version(parsed.get('Version')),
                "Product Name": parsed.get('Product Name', ''),
                "Product ID": parsed.get('Product ID', ''),
                "Installed Key": parsed.get('Installed Key', ''),
                "Original Key": parsed.get('Original Key', ''),
                "OEM Key": parsed.get('OEM Key', ''),
                "Original Edition": parsed.get('Original Edition', '')
            }

            all_data.append(row_data)
            print(f"准备上传：{filename}")

    if all_data:
        upload_to_sheet(all_data)
        print("全部上传完成。")
    else:
        print("没有找到可处理的 .txt 文件。")

# 示例：指定文件夹路径
if __name__ == '__main__':
    folder_path = r'K:\romeo\11_Users\Q\TOOLS\ShowKeyPlus_x86'
    main(folder_path)
