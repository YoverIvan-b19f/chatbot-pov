import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GoogleSheetsHelper:
    def __init__(self):
        self.credentials_file = os.getenv('GOOGLE_SHEETS_CREDENTIALS', 'credentials.json')
        self.spreadsheet_id = os.getenv('SPREADSHEET_ID')
        self.client = None
        self.sheet = None
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize Google Sheets client"""
        try:
            if not os.path.exists(self.credentials_file):
                logger.warning(f"Credentials file {self.credentials_file} not found")
                return
            
            # Intentar importar gspread solo si es necesario
            try:
                import gspread
                from google.oauth2.service_account import Credentials
            except ImportError:
                logger.warning("gspread no instalado. Google Sheets no disponible.")
                return
            
            # Define the scope
            scope = ['https://www.googleapis.com/auth/spreadsheets']
            
            # Load credentials
            creds = Credentials.from_service_account_file(
                self.credentials_file, scopes=scope
            )
            
            # Authorize and create client
            self.client = gspread.authorize(creds)
            
            # Open the spreadsheet
            if self.spreadsheet_id:
                self.sheet = self.client.open_by_key(self.spreadsheet_id).sheet1
                logger.info("Google Sheets client initialized successfully")
            else:
                logger.warning("SPREADSHEET_ID not set in environment variables")
                
        except Exception as e:
            logger.error(f"Error initializing Google Sheets client: {str(e)}")
            self.sheet = None
    
    def save_profile(self, anonymized_id, answers, profile, timestamp=None):
        """Save a user profile to Google Sheets"""
        if not self.sheet:
            logger.warning("Google Sheets client not initialized. Profile not saved.")
            return False
        
        try:
            # Prepare row data
            if timestamp is None:
                timestamp = datetime.now()
            
            # Create row with timestamp, anonymized_id, answers, and profile
            row_data = [
                timestamp.strftime("%Y-%m-%d %H:%M:%S"),  # Timestamp
                anonymized_id,  # Anonymized ID
            ]
            
            # Add answers (8 questions)
            for i in range(1, 9):
                answer_key = f'question_{i}'
                row_data.append(answers.get(answer_key, ''))
            
            # Add profile
            row_data.append(profile)  # Complete profile text
            
            # Append to sheet
            self.sheet.append_row(row_data)
            logger.info(f"Profile saved for user {anonymized_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving profile to Google Sheets: {str(e)}")
            return False
    
    def get_stats(self):
        """Get statistics from Google Sheets"""
        if not self.sheet:
            return None
        
        try:
            records = self.sheet.get_all_records()
            total_profiles = len(records)
            return {
                'total_profiles': total_profiles,
                'last_update': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting stats from Google Sheets: {str(e)}")
            return None