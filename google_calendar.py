import os
import pickle
import datetime
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pytz
from datetime import datetime, timedelta
from googleapiclient.errors import HttpError
import pytz

# SCOPES = ['https://www.googleapis.com/auth/calendar']
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def authenticate_google_account():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run.
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def create_google_calendar_event(candidate_email, interviewer_email, date, time, timezone):
    creds = authenticate_google_account()

    service = build('calendar', 'v3', credentials=creds)

    start_time_str = f"{date}T{time}:00"
    
    try:
        start_time = datetime.strptime(start_time_str, "%Y-%m-%dT%H:%M:%S")
        local_tz = pytz.timezone(timezone)
        start_time = local_tz.localize(start_time)

        end_time = start_time + timedelta(hours=1)

        event = {
            'summary': f'Interview: {candidate_email} with {interviewer_email}',
            'location': 'Online',
            'description': 'Interview for the job position.',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': timezone,
            },
            'attendees': [
                {'email': candidate_email},
                {'email': interviewer_email},
            ],
            'reminders': {
                'useDefault': True,
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': f"{candidate_email}-{interviewer_email}-{start_time_str}",
                    'conferenceSolutionKey': {
                        'type': 'hangoutsMeet',
                    },
                },
            },
        }

        event = service.events().insert(
            calendarId='primary', body=event, conferenceDataVersion=1
        ).execute()

        calendar_link = event.get('htmlLink')
        meet_link = event['conferenceData']['entryPoints'][0]['uri']

        return meet_link, calendar_link

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None, None


