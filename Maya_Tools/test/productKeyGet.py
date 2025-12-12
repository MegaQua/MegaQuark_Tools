import platform
import getpass
import socket
import subprocess
from datetime import datetime
import winreg
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Google Sheets 配置
SPREADSHEET_ID = '1MoPoarQkDNVdOHGfmO0Ong7fyZCrAynARCKHyYDhkEc'
RANGE_NAME = 'Sheet1'
SERVICE_ACCOUNT_FILE = 'S:/Public/qiu_yi/JCQ_Tool/data/project-gomapy-d737ea76a8ff.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# 获取 OEM Key 和 Product Key
def decode_product_key(key_bytes):
    key_offset = 52
    key_chars = "BCDFGHJKMPQRTVWXY2346789"
    decoded_chars = []
    key_bytes = key_bytes[key_offset:key_offset + 15]
    for i in range(25):
        current = 0
        for j in range(14, -1, -1):
            current = current * 256
            current += key_bytes[j]
            key_bytes[j] = current // 24
            current %= 24
        decoded_chars.insert(0, key_chars[current])
    for i in range(5, 25, 6):
        decoded_chars.insert(i, '-')
    return ''.join(decoded_chars)

def get_product_key():
    try:
        path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        hkey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
        digital_product_id, _ = winreg.QueryValueEx(hkey, "DigitalProductId")
        return decode_product_key(bytearray(digital_product_id))
    except Exception:
        return "N/A"

def get_oem_key():
    try:
        output = subprocess.check_output(
            ['wmic', 'path', 'softwarelicensingservice', 'get', 'OA3xOriginalProductKey'],
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL
        ).decode().split('\n')
        if len(output) > 1:
            return output[1].strip()
    except:
        return "N/A"
def get_display_name():
    try:
        import subprocess
        result = subprocess.check_output(
            ['powershell', '-Command',
             "(Get-WmiObject Win32_UserAccount | Where-Object { $_.Name -eq $env:USERNAME }).FullName"],
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            shell=True
        ).decode('utf-8').strip()
        return result if result else "N/A"
    except Exception:
        return "N/A"

def get_info():
    current_user = getpass.getuser()

    try:
        import os
        local_user = os.path.basename(os.path.expanduser("~"))
    except:
        local_user = "N/A"

    display = get_display_name()  # ✅ 正确调用

    return {
        "Computer Name": platform.node(),
        "User Name": current_user,
        "Local Account Name": local_user,
        "Display Name": display,
        "Windows Version": platform.platform(),
        "Product Key": get_product_key(),
        "OEM Key": get_oem_key(),
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        #"IP Address": socket.gethostbyname(socket.gethostname())
    }

# 上传数据到 Google 表格
def upload_to_sheet(data: dict):
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()

    # 先获取当前表格已有内容
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    rows = result.get('values', [])

    # 如果第一行为空，先写入标题
    if not rows:
        header = list(data.keys())
        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body={'values': [header]}
        ).execute()

    # 写入数据
    values = [list(data.values())]
    sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME,
        valueInputOption='RAW',
        insertDataOption='INSERT_ROWS',
        body={'values': values}
    ).execute()

# 主函数
if __name__ == '__main__':
    info = get_info()
    print("Info collected:\n", info)
    upload_to_sheet(info)
