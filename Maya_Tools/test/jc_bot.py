from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
import os.path
import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
JsonKey = 'S:\Public\qiu_yi\JCQ_Tool\data/client_secret_483253873254-di4nv291hq6db6alhsd76rivkmps711q.apps.googleusercontent.com.json'

def get_events_from_calendar(service, calendar_id):
    # 获取现在时间
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' 表示 UTC 时间

    # 获取日历中的事件
    print(f'获取日历 {calendar_id} 中的事件')
    events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                          maxResults=100, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('没有即将发生的事件。')
        return

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

def main():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(JsonKey, SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # 替换为你的日历ID
    specific_calendar_id = 'for-the-cause.com_a9srrrnr6n8ia2jrvrhhj2u70k@group.calendar.google.com'
    get_events_from_calendar(service, specific_calendar_id)

if __name__ == '__main__':
    main()
