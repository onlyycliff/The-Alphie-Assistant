import logging
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

logger = logging.getLogger(__name__)


def get_credentials(token_path: str, scopes: list[str]) -> Credentials:
    """Loads or creates OAuth credentials for a Google API, persisting them to token_path."""
    creds = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", scopes)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as token:
            token.write(creds.to_json())
        try:
            os.chmod(token_path, 0o600)
        except OSError:
            logger.debug("Could not restrict permissions on %s", token_path)

    return creds
