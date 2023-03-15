from google.oauth2 import service_account
from apiclient.discovery import build
from parser import Entry
import datetime

CALENDAR_ID = "vintrob.simon@gmail.com"
SCOPES = ['https://www.googleapis.com/auth/calendar']
KEY_FILE_LOCATION = '../creds/svc_acc_calendar.json'


creds = service_account.Credentials.from_service_account_file(
      KEY_FILE_LOCATION, scopes=SCOPES)

service = build('calendar', 'v3', credentials=creds)

def add_event(e: Entry):
    start = e.tiempo.tiempo.isoformat()
    end   = (e.tiempo.tiempo + datetime.timedelta(minutes=30)).isoformat()

    event = {
        'summary': e.texto_limpito, 
        'start': {
          'dateTime': start, 
          'timeZone': 'America/Argentina/Buenos_Aires',
        },
        'end': {
          'dateTime': end,
          'timeZone': 'America/Argentina/Buenos_Aires',
        },
        'reminders': {
          'useDefault': False,
          'overrides': [
            {'method': 'popup', 'minutes': 10},
          ],
        },
      } 
    service.events().insert(calendarId=e.calendarId if e.calendarId else CALENDAR_ID, body=event).execute()

