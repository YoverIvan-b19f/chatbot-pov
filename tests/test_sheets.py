import os
from dotenv import load_dotenv
from utils.sheets import GoogleSheetsHelper
from datetime import datetime

load_dotenv()

def test_sheets_connection():
    """Test Google Sheets connection"""
    sheets = GoogleSheetsHelper()
    
    if sheets.sheet:
        print("✅ Google Sheets connection successful!")
        stats = sheets.get_stats()
        if stats:
            print(f"📊 Current stats: {stats}")
        return True
    else:
        print("❌ Google Sheets connection failed")
        return False

def test_save_profile():
    """Test saving a profile to Google Sheets"""
    sheets = GoogleSheetsHelper()
    
    if not sheets.sheet:
        print("❌ Cannot test: Google Sheets not connected")
        return False
    
    # Test data
    test_answers = {
        'question_1': 'Matemáticas',
        'question_2': 'Resolver problemas',
        'question_3': 'Leer',
        'question_4': 'Me encanta',
        'question_5': 'Ayudar a otros',
        'question_6': 'Liderazgo',
        'question_7': 'Educación',
        'question_8': 'Escuela'
    }
    
    test_profile = """
    Carreras recomendadas:
    1. Ingeniería de Sistemas
    2. Educación
    3. Administración
    
    Instituciones: UNC, UPN
    
    Vías de acceso: Beca 18
    """
    
    success = sheets.save_profile(
        anonymized_id='1234',
        answers=test_answers,
        profile=test_profile
    )
    
    if success:
        print("✅ Profile saved successfully!")
        return True
    else:
        print("❌ Failed to save profile")
        return False

if __name__ == "__main__":
    print("🧪 Testing Google Sheets...")
    
    # Test connection
    print("\n1️⃣ Testing connection...")
    connection_ok = test_sheets_connection()
    
    # Test save profile
    if connection_ok:
        print("\n2️⃣ Testing save profile...")
        test_save_profile()