import logging

import google_auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    """Shows basic usage of the Gmail API.
    Return the user's service.
    """
    creds = google_auth.get_credentials('token.json', SCOPES)

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        return service

    except HttpError as error:
        logger.error('An error occurred: %s', error)
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
        logger.error('An error occurred: %s', error)
        return f'Error retrieving unread emails: {error}'

if __name__ == '__main__':
    service = get_gmail_service()
    if service:
        print("Gmail service created successfully.")
    else:
        print("Failed to create Gmail service.")
    