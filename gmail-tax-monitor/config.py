#!/usr/bin/env python3
"""
Configuration for Gmail Tax Monitor
"""

import os
from datetime import datetime

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Create directories if they don't exist
for directory in [DATA_DIR, LOGS_DIR]:
    os.makedirs(directory, exist_ok=True)

# Tax-related keywords to monitor
TAX_KEYWORDS = [
    # Australian Tax Office
    'ATO', 'Australian Tax Office', 'tax return', 'tax assessment',
    'BAS', 'Business Activity Statement', 'GST', 'income tax',
    'tax invoice', 'tax statement', 'notice of assessment',
    
    # ASIC
    'ASIC', 'Australian Securities and Investments Commission',
    'company registration', 'annual review', 'lodgement',
    
    # SMSF
    'SMSF', 'Self Managed Super Fund', 'superannuation',
    'SMSF audit', 'SMSF return', 'super fund',
    
    # Bills and Invoices
    'invoice', 'receipt', 'bill', 'payment',
    'statement', 'account', 'due', 'overdue',
    
    # Financial Institutions
    'bank statement', 'credit card', 'loan statement',
    'mortgage', 'interest', 'dividend',
    
    # Property
    'rental', 'property tax', 'land tax', 'council rates',
    
    # Business
    'ABN', 'TFN', 'business', 'company', 'partnership',
    
    # Legal
    'legal', 'contract', 'agreement', 'compliance'
]

# Sender domains to prioritize
PRIORITY_SENDERS = [
    'ato.gov.au',
    'asic.gov.au',
    'smsf.gov.au',
    'my.gov.au',
    'abs.gov.au',
    
    # Banks
    'commbank.com.au',
    'westpac.com.au',
    'nab.com.au',
    'anz.com.au',
    
    # Accounting software
    'xero.com',
    'myob.com',
    'quickbooks.com',
    
    # Utilities
    'originenergy.com.au',
    'agl.com.au',
    'energyaustralia.com.au',
    'telstra.com',
    'optus.com.au'
]

# File types to save (invoice attachments)
INVOICE_FILE_TYPES = [
    '.pdf',
    '.xlsx', '.xls',
    '.docx', '.doc',
    '.jpg', '.jpeg', '.png',
    '.csv',
    '.txt'
]

# Email search query (Gmail search syntax)
SEARCH_QUERY = ' OR '.join([f'"{keyword}"' for keyword in TAX_KEYWORDS[:20]])  # Limit to 20 for query length

# Processing settings
MAX_EMAILS_PER_RUN = 100
DAYS_TO_CHECK = 7  # Check emails from last 7 days

# Storage organization
def get_storage_path(category, filename=None):
    """Get organized storage path for files."""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Category folders
    category_folders = {
        'ATO': 'ATO',
        'ASIC': 'ASIC',
        'SMSF': 'SMSF',
        'Bills': 'Bills',
        'Bank': 'Bank_Statements',
        'Property': 'Property',
        'Business': 'Business',
        'Other': 'Other'
    }
    
    category_folder = category_folders.get(category, 'Other')
    category_path = os.path.join(DATA_DIR, category_folder, today)
    os.makedirs(category_path, exist_ok=True)
    
    if filename:
        return os.path.join(category_path, filename)
    return category_path

# Logging
LOG_FILE = os.path.join(LOGS_DIR, f'monitor_{datetime.now().strftime("%Y%m")}.log')

# Email processing flags
MARK_AS_READ = True
ADD_LABEL = 'Tax-Documents'
CREATE_LABEL = True