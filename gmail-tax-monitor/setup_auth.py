#!/usr/bin/env python3
"""
Gmail API Authentication Setup
Run this script first to authenticate and get tokens.
"""

import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.pickle.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

def main():
    """Shows basic usage of the Gmail API."""
    creds = None
    
    # The file token.pickle stores the user's access and refresh tokens.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("Error: credentials.json not found!")
                print("Please download it from Google Cloud Console and place it in this directory.")
                return
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    # Test the connection
    try:
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().getProfile(userId='me').execute()
        print(f"✅ Successfully authenticated as: {results['emailAddress']}")
        print("✅ Authentication complete! You can now run the monitor script.")
    except Exception as e:
        print(f"❌ Authentication failed: {e}")

if __name__ == '__main__':
    main()