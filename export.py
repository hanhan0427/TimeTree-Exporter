import os
import requests
import icalendar
from googleapiclient.discovery import build
from google.oauth2 import service_account
from github import Github

# GitHub 相關設定
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPOSITORY")
ARTIFACT_NAME = "calendar.ics"  # 更改成你的artifact檔案名稱

# Google Calendar 相關設定
CALENDAR_ID = 'YOUR_CALENDAR_ID'
SERVICE_ACCOUNT_FILE = 'service_account.json'  # 假設金鑰檔案在倉庫中

# 設定 Google Calendar API 憑證
SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

# 建立 Google Calendar API 服務
service = build('calendar', 'v3', credentials=creds)


def download_artifact(repo_name, artifact_name, github_token):
    """Download the artifact from GitHub Actions."""
    g = Github(github_token)
    repo = g.get_repo(repo_name)
    actions = repo.get_actions()

    artifacts = repo.get_artifacts()
    for artifact in artifacts:
        if artifact.name == artifact_name:
            print(f"Downloading artifact: {artifact.name}")
            download = artifact.download_artifact()
            with open(artifact_name, "wb") as f:
                f.write(download.data)
            print(f"Artifact downloaded to {artifact_name}")
            return artifact_name
    return None


def parse_ics_file(ics_filepath):
    """Parse the ICS file and return a list of events."""
    with open(ics_filepath, 'r', encoding='utf-8') as f:
        calendar = icalendar.Calendar.from_ical(f.read())
    events = []
    for component in calendar.walk():
        if component.name == "VEVENT":
            event = {
                'summary': component.get('summary'),
                'location': component.get('location'),
                'description': component.get('description'),
                'start': component.get('dtstart').to_rfc3339(),
                'end': component.get('dtend').to_rfc3339(),
            }
            events.append(event)
    return events


def create_google_calendar_event(service, calendar_id, event):
    """Create an event in Google Calendar."""
    event_body = {
        'summary': event['summary'],
        'location': event['location'],
        'description': event['description'],
        'start': {
            'dateTime': event['start'],
            'timeZone': 'Asia/Taipei',  # 替換成你的時區
        },
        'end': {
            'dateTime': event['end'],
            'timeZone': 'Asia/Taipei',  # 替換成你的時區
        },
    }
    event = service.events().insert(calendarId=calendar_id, body=event_body).execute()
    print(f"Event created: {event.get('htmlLink')}")


def main():
    """Main function."""
    # 下載 artifact
    ics_file = download_artifact(GITHUB_REPO, ARTIFACT_NAME, GITHUB_TOKEN)
    if not ics_file:
        print(f"Artifact {ARTIFACT_NAME} not found.")
        return

    # 解析 ICS 檔案
    events = parse_ics_file(ics_file)

    # 將事件導入 Google Calendar
    for event in events:
        create_google_calendar_event(service, CALENDAR_ID, event)


if __name__ == '__main__':
    main()
