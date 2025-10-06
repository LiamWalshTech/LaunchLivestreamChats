import os
import google_auth_oauthlib.flow
from googleapiclient.discovery import build

def main():
    print("Welcome to Launch Livestream Chats")
    
    # Define the scopes (adjust based on your needs)
    scopes = ['https://www.googleapis.com/auth/youtube.readonly']  # Example; use 'https://www.googleapis.com/auth/youtube' for write access

    # Path to client secrets file
    client_secrets_file = './youtube-credentials.json'

    # Initialize the flow without a redirect URI
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)

    # Get the authorization URL for manual flow
    auth_url, state = flow.authorization_url(prompt='consent')

    print(f"Please open this URL in your browser and authorize the app: {auth_url}")
    code = input("Enter the authorization code from the browser: ")

    # Exchange the authorization code for credentials
    flow.fetch_token(code=code)
    credentials = flow.credentials

    # Build the YouTube API service
    youtube = build('youtube', 'v3', credentials=credentials)

    # Example API call: List channels
    request = youtube.channels().list(part="contentDetails", mine=True)
    response = request.execute()
    print(response)

if __name__ == '__main__':
    main()
