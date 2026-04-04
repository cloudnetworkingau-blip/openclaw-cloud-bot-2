#!/usr/bin/env python3
"""
Gmail Tax Monitor - Main script
Monitors tax-related emails and saves invoices.
"""

import os
import pickle
import base64
import email
import re
import logging
from datetime import datetime, timedelta
from email.header import decode_header
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GmailTaxMonitor:
    def __init__(self):
        self.service = self.authenticate_gmail()
        self.label_id = None
        
    def authenticate_gmail(self):
        """Authenticate and return Gmail service."""
        creds = None
        
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                logger.error("No valid credentials found. Please run setup_auth.py first.")
                return None
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        try:
            service = build('gmail', 'v1', credentials=creds)
            logger.info("✅ Gmail authentication successful")
            return service
        except Exception as e:
            logger.error(f"❌ Authentication failed: {e}")
            return None
    
    def get_or_create_label(self):
        """Get or create the Tax-Documents label."""
        if self.label_id:
            return self.label_id
        
        try:
            # Try to get existing label
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            for label in labels:
                if label['name'] == config.ADD_LABEL:
                    self.label_id = label['id']
                    logger.info(f"Found existing label: {config.ADD_LABEL}")
                    return self.label_id
            
            # Create new label
            if config.CREATE_LABEL:
                label_body = {
                    'name': config.ADD_LABEL,
                    'labelListVisibility': 'labelShow',
                    'messageListVisibility': 'show'
                }
                label = self.service.users().labels().create(userId='me', body=label_body).execute()
                self.label_id = label['id']
                logger.info(f"Created new label: {config.ADD_LABEL}")
                return self.label_id
            
        except Exception as e:
            logger.error(f"Error managing label: {e}")
        
        return None
    
    def decode_subject(self, subject):
        """Decode email subject."""
        if not subject:
            return "No Subject"
        
        decoded_parts = decode_header(subject)
        decoded = []
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                if encoding:
                    decoded.append(part.decode(encoding))
                else:
                    decoded.append(part.decode('utf-8', errors='ignore'))
            else:
                decoded.append(part)
        
        return ' '.join(decoded)
    
    def get_email_details(self, message):
        """Extract email details."""
        headers = message['payload']['headers']
        details = {
            'subject': '',
            'from': '',
            'date': '',
            'to': ''
        }
        
        for header in headers:
            name = header['name'].lower()
            if name == 'subject':
                details['subject'] = self.decode_subject(header['value'])
            elif name == 'from':
                details['from'] = header['value']
            elif name == 'date':
                details['date'] = header['value']
            elif name == 'to':
                details['to'] = header['value']
        
        return details
    
    def categorize_email(self, subject, sender):
        """Categorize email based on content and sender."""
        subject_lower = subject.lower()
        sender_lower = sender.lower()
        
        # Check sender domains
        for domain in config.PRIORITY_SENDERS:
            if domain in sender_lower:
                if 'ato.gov.au' in domain:
                    return 'ATO'
                elif 'asic.gov.au' in domain:
                    return 'ASIC'
                elif 'smsf.gov.au' in domain:
                    return 'SMSF'
                elif any(bank in domain for bank in ['commbank', 'westpac', 'nab', 'anz']):
                    return 'Bank'
        
        # Check keywords in subject
        if any(keyword.lower() in subject_lower for keyword in ['ATO', 'tax', 'assessment', 'BAS', 'GST']):
            return 'ATO'
        elif any(keyword.lower() in subject_lower for keyword in ['ASIC', 'company', 'registration']):
            return 'ASIC'
        elif any(keyword.lower() in subject_lower for keyword in ['SMSF', 'super', 'superannuation']):
            return 'SMSF'
        elif any(keyword.lower() in subject_lower for keyword in ['invoice', 'bill', 'payment', 'receipt']):
            return 'Bills'
        elif any(keyword.lower() in subject_lower for keyword in ['rent', 'property', 'council']):
            return 'Property'
        elif any(keyword.lower() in subject_lower for keyword in ['business', 'ABN', 'company']):
            return 'Business'
        
        return 'Other'
    
    def save_attachment(self, attachment_data, filename, category):
        """Save attachment to organized folder."""
        try:
            # Clean filename
            filename = re.sub(r'[^\w\-_. ]', '_', filename)
            
            # Ensure unique filename
            base, ext = os.path.splitext(filename)
            counter = 1
            original_filename = filename
            
            storage_path = config.get_storage_path(category, filename)
            
            while os.path.exists(storage_path):
                filename = f"{base}_{counter}{ext}"
                storage_path = config.get_storage_path(category, filename)
                counter += 1
            
            # Save file
            with open(storage_path, 'wb') as f:
                f.write(attachment_data)
            
            logger.info(f"Saved attachment: {filename} to {category}")
            return storage_path
            
        except Exception as e:
            logger.error(f"Error saving attachment {filename}: {e}")
            return None
    
    def process_attachments(self, message, category):
        """Process and save email attachments."""
        saved_files = []
        
        def process_part(part):
            if part.get('filename'):
                filename = part['filename']
                file_ext = os.path.splitext(filename)[1].lower()
                
                if file_ext in config.INVOICE_FILE_TYPES:
                    if 'data' in part['body']:
                        data = part['body']['data']
                    elif 'attachmentId' in part['body']:
                        att_id = part['body']['attachmentId']
                        att = self.service.users().messages().attachments().get(
                            userId='me', messageId=message['id'], id=att_id).execute()
                        data = att['data']
                    else:
                        return
                    
                    file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
                    saved_path = self.save_attachment(file_data, filename, category)
                    if saved_path:
                        saved_files.append(saved_path)
            
            if 'parts' in part:
                for subpart in part['parts']:
                    process_part(subpart)
        
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                process_part(part)
        elif 'filename' in message['payload']:
            process_part(message['payload'])
        
        return saved_files
    
    def search_tax_emails(self):
        """Search for tax-related emails."""
        try:
            # Calculate date range
            days_ago = (datetime.now() - timedelta(days=config.DAYS_TO_CHECK)).strftime('%Y/%m/%d')
            date_query = f'after:{days_ago}'
            
            # Combine search queries
            full_query = f'({config.SEARCH_QUERY}) {date_query}'
            
            logger.info(f"Searching for: {full_query}")
            
            results = self.service.users().messages().list(
                userId='me',
                q=full_query,
                maxResults=config.MAX_EMAILS_PER_RUN
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} tax-related emails")
            return messages
            
        except Exception as e:
            logger.error(f"Error searching emails: {e}")
            return []
    
    def process_email(self, msg_id):
        """Process a single email."""
        try:
            # Get full message
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()
            
            # Get email details
            details = self.get_email_details(message)
            category = self.categorize_email(details['subject'], details['from'])
            
            logger.info(f"Processing: {details['subject'][:50]}... | From: {details['from']} | Category: {category}")
            
            # Process attachments
            saved_files = self.process_attachments(message, category)
            
            # Mark as read and add label
            if config.MARK_AS_READ or config.ADD_LABEL:
                modify_body = {}
                
                if config.MARK_AS_READ:
                    modify_body['removeLabelIds'] = ['UNREAD']
                
                if config.ADD_LABEL and self.label_id:
                    if 'addLabelIds' not in modify_body:
                        modify_body['addLabelIds'] = []
                    modify_body['addLabelIds'].append(self.label_id)
                
                if modify_body:
                    self.service.users().messages().modify(
                        userId='me',
                        id=msg_id,
                        body=modify_body
                    ).execute()
            
            return {
                'id': msg_id,
                'subject': details['subject'],
                'from': details['from'],
                'date': details['date'],
                'category': category,
                'saved_files': saved_files,
                'processed': True
            }
            
        except Exception as e:
            logger.error(f"Error processing email {msg_id}: {e}")
            return {
                'id': msg_id,
                'error': str(e),
                'processed': False
            }
    
    def run(self):
        """Main monitoring function."""
        if not self.service:
            logger.error("Gmail service not available. Authentication failed.")
            return
        
        logger.info("🚀 Starting Gmail Tax Monitor")
        
        # Get or create label
        if config.ADD_LABEL:
            self.get_or_create_label()
        
        # Search for tax emails
        messages = self.search_tax_emails()
        
        if not messages:
            logger.info("No tax-related emails found.")
            return
        
        # Process each email
        results = []
        for msg in messages:
            result = self.process_email(msg['id'])
            results.append(result)
        
        # Summary
        processed = sum(1 for r in results if r.get('processed'))
        saved_files = sum(len(r.get('saved_files', [])) for r in results)
        
        logger.info(f"✅ Processing complete: {processed}/{len(messages)} emails processed, {saved_files} files saved")
        
        return results

def main():
    """Main entry point."""
    monitor = GmailTaxMonitor()
    return monitor.run()

if __name__ == '__main__':
    main()