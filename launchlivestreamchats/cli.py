import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
import os
import json
import sys
import webbrowser

# Define the scopes (read-only access to live broadcasts)
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

# Paths to credentials files
CLIENT_SECRETS_FILE = './youtube-credentials.json'
TOKEN_FILE = 'token.json'

def get_youtube_credentials():
    credentials = None
    print(f"Checking for token file: {TOKEN_FILE}")
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as token:
            try:
                data = json.load(token)
                if isinstance(data, dict) and 'access_token' in data:
                    credentials = data
                    print("Token file loaded, validating credentials")
                else:
                    print("Token file content invalid, re-authenticating")
                    os.remove(TOKEN_FILE)
            except json.JSONDecodeError:
                print("Token file corrupted, re-authenticating")
                os.remove(TOKEN_FILE)

    if not credentials or not credentials.get('refresh_token'):
        print(f"Credentials invalid or missing, loading from {CLIENT_SECRETS_FILE}")
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, SCOPES)
        print("Starting OAuth flow")
        credentials = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            json.dump(credentials.to_json(), token, indent=2)
            print("Saved new credentials to token file")
    return credentials

def get_youtube_livestream_id():
    credentials = get_youtube_credentials()
    print("Building YouTube API client")
    youtube = build('youtube', 'v3', credentials=credentials)

    try:
        print("Executing API request for current livestream")
        # Request live broadcasts with mine=True
        request = youtube.liveBroadcasts().list(
            part='id,snippet,status',
            mine=True,
            maxResults=10  # Adjust if you have many broadcasts
        )
        response = request.execute()

        # Find the current livestream
        current_livestream_id = None
        if 'items' in response:
            for item in response['items']:
                status = item['status']
                if status.get('lifeCycleStatus') == 'live':
                    current_livestream_id = item['id']
                    break

        if current_livestream_id:
            return current_livestream_id
        else:
            print("No active livestream found. Ensure you have a live broadcast running.")

    except HttpError as e:
        print(f"API error: {e}")

def get_youtube_livestream_chat_url():
    youtube_livestream_id = get_youtube_livestream_id()

    return f"https://studio.youtube.com/live_chat?is_popout=1&v={youtube_livestream_id}"

def open_browser_with_url(url):
    print(f"Opening browser with URL: {url}")
    webbrowser.open(url, new=1)

if __name__ == '__main__':
    youtube_livestream_chat_url = get_youtube_livestream_chat_url()
    open_browser_with_url(youtube_livestream_chat_url)
    sys.exit(0)
