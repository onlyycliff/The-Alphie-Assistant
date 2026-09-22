import datetime
import logging

import google_auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file gcalendar_token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def get_calendar_service():
  """Shows basic usage of the Google Calendar API.
    Return the user's service.
  """
  creds = google_auth.get_credentials("gcalendar_token.json", SCOPES)

  try:
    service = build("calendar", "v3", credentials=creds)
    return service
  except HttpError as error:
    logger.error("An error occurred: %s", error)
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
        logger.error("An error occurred: %s", error)
        return f'Error retrieving upcoming events: {error}'


if __name__ == "__main__":
  service = get_calendar_service()
  if service:
      print(f"Successfully connected to Google Calendar API.{service}")
  else:
      print(f"An error occurred while connecting to Google Calendar API.")
