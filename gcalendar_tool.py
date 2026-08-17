import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file gcalendar_token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def get_calendar_service():
  """Shows basic usage of the Google Calendar API.
    Return the user's service.
  """
  creds = None
  # The file gcalendar_token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("gcalendar_token.json"):
    creds = Credentials.from_authorized_user_file("gcalendar_token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("gcalendar_token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)
    return service
  except HttpError as error:
    print(f"An error occurred: {error}")
    return None

def get_upcoming_events(service, max_results=10):
    """Get a list of upcoming events."""
    try:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])
    
        if not events:
            return "No upcoming events found."
        
        event_list = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            event_list.append(f"{start} - {event['summary']}")
        return "\n".join(event_list)
    
    except HttpError as error:
        print(f"An error occurred: {error}")
        return f'Error retrieving upcoming events: {error}'


if __name__ == "__main__":
  service = get_calendar_service()
  if service:
      print(f"Successfully connected to Google Calendar API.{service}")
  else:
      print(f"An error occurred while connecting to Google Calendar API.")
