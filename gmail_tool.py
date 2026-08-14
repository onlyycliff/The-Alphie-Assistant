import os.path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Shows basic usage of the Gmail API.
    Return the user's service.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            
    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        return service
    
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def get_unread_emails(service):
    """Get a list of unread emails."""
    try:
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q='is:unread').execute()
        messages = results.get('messages', [])
        
        if not messages:
            return f'No unread emails found.'
        else:
            unread_list = []
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                subject = ''
                for header in msg['payload']['headers']:
                    if header['name'] == 'Subject':
                        subject = header['value']
                        break
                unread_list.append(subject)
            return "\n".join(unread_list)
            
            
        
    except HttpError as error:
        print(f'An error occurred: {error}')
        return f'Error retrieving unread emails: {error}'

if __name__ == '__main__':
    service = get_gmail_service()
    if service:
        print("Gmail service created successfully.")
    else:
        print("Failed to create Gmail service.")
    