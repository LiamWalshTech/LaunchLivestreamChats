from dotenv import load_dotenv, set_key
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
import json
import os
import sys
import webbrowser
from getpass import getpass

# Define the path for the .env file
ENV_FILE = '.env'

# Load existing environment variables (if any)
load_dotenv(ENV_FILE)

def prompt_and_store_credentials():
    print("Please enter your credentials (leave blank to keep existing values):")
    
    # Prompt for client secrets JSON content
    current_path = os.getenv('CLIENT_SECRETS_PATH', './youtube-credentials.json')
    client_secrets_content = input(f"Paste the client_secrets.json content [press Enter to keep {current_path}]: ")
    if client_secrets_content:
        try:
            json.loads(client_secrets_content)  # Validate JSON
            with open('./youtube-credentials.json', 'w') as output_file:
                output_file.write(client_secrets_content)
            set_key(ENV_FILE, 'CLIENT_SECRETS_PATH', './youtube-credentials.json')
            print("Client secrets JSON saved to ./youtube-credentials.json.")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON content: {e}. Using existing file at {current_path}.")
    else:
        print(f"Keeping existing client secrets file at {current_path}.")

    # Prompt for Twitch channel name
    twitch_channel = input(f"Twitch Channel Name [default: {os.getenv('TWITCH_CHANNEL_NAME', '')}]: ") or os.getenv('TWITCH_CHANNEL_NAME', '')
    if twitch_channel:
        set_key(ENV_FILE, 'TWITCH_CHANNEL_NAME', twitch_channel)

    # Prompt for X user handle
    x_handle = input(f"X User Handle [default: {os.getenv('X_USER_HANDLE', '')}]: ") or os.getenv('X_USER_HANDLE', '')
    if x_handle:
        set_key(ENV_FILE, 'X_USER_HANDLE', x_handle)

    # Prompt for YouTube API key (masked, no default shown)
    api_key = getpass("YouTube API Key (optional, leave blank if not needed): ")
    if api_key:
        set_key(ENV_FILE, 'YOUTUBE_API_KEY', api_key)

    print(f"Credentials saved to {ENV_FILE}.")

def get_youtube_credentials():
    credentials = None
    TOKEN_FILE = 'token.json'
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
        client_secrets_path = os.getenv('CLIENT_SECRETS_PATH', './youtube-credentials.json')
        print(f"Credentials invalid or missing, loading from {client_secrets_path}")
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_path, ['https://www.googleapis.com/auth/youtube.readonly'])
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
        request = youtube.liveBroadcasts().list(
            part='id,snippet,status',
            mine=True,
            maxResults=10
        )
        response = request.execute()

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
            return None

    except HttpError as e:
        print(f"API error: {e}")
        return None

def get_youtube_livestream_chat_url():
    youtube_livestream_id = get_youtube_livestream_id()
    if youtube_livestream_id:
        return f"https://studio.youtube.com/live_chat?is_popout=1&v={youtube_livestream_id}"
    else:
        print("Skipping YouTube chat: No livestream ID found.")
        return None

def get_twitch_livestream_chat_url():
    twitch_channel = os.getenv('TWITCH_CHANNEL_NAME')
    if twitch_channel:
        return f"https://www.twitch.tv/popout/{twitch_channel}/chat?popout="
    else:
        print("Skipping Twitch chat: TWITCH_CHANNEL_NAME not set in .env.")
        return None

def get_x_livestream_chat_url():
    x_handle = os.getenv('X_USER_HANDLE')
    if x_handle:
        return f"https://x.com/{x_handle}/chat"
    else:
        print("Skipping X chat: X_USER_HANDLE not set in .env.")
        return None

def open_browser_with_url(url):
    if url:
        print(f"Opening browser with URL: {url}")
        webbrowser.open(url, new=1)
    else:
        print("No URL provided, skipping browser open.")

if __name__ == '__main__':
    # Prompt for credentials if .env is missing or user wants to update
    if not os.path.exists(ENV_FILE) or input("Update credentials? (yes/no): ").lower() in ['yes', 'y']:
        prompt_and_store_credentials()
    load_dotenv(ENV_FILE)  # Reload after potential update

    youtube_livestream_chat_url = get_youtube_livestream_chat_url()
    twitch_livestream_chat_url = get_twitch_livestream_chat_url()
    x_livestream_chat_url = get_x_livestream_chat_url()

    open_browser_with_url(youtube_livestream_chat_url)
    open_browser_with_url(twitch_livestream_chat_url)
    open_browser_with_url(x_livestream_chat_url)

    sys.exit(0)
