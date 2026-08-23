#!/usr/bin/env python
"""
Script para configurar Google Sheets
Crea la estructura inicial de la hoja
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Agregar directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.sheets import GoogleSheetsHelper
from utils.validators import format_phone_number

load_dotenv()

def setup_sheets():
    """Configura la estructura inicial de Google Sheets"""
    print("📊 Configurando Google Sheets...")
    
    sheets = GoogleSheetsHelper()
    
    if not sheets.sheet:
        print("❌ No se pudo conectar con Google Sheets")
        print("Verifica que credentials.json y SPREADSHEET_ID estén configurados")
        return False
    
    try:
        # Verificar si la hoja tiene encabezados
        headers = sheets.sheet.row_values(1)
        
        if not headers:
            # Crear encabezados
            headers = [
                "Timestamp",
                "ID Anonimizado",
                "Pregunta 1",
                "Pregunta 2",
                "Pregunta 3",
                "Pregunta 4",
                "Pregunta 5",
                "Pregunta 6",
                "Pregunta 7",
                "Pregunta 8",
                "Perfil Generado",
                "Fecha de Registro"
            ]
            
            sheets.sheet.append_row(headers)
            print("✅ Encabezados creados correctamente")
        
        # Agregar datos de prueba
        test_data = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "1234",
            "Matemáticas",
            "Resolver problemas",
            "Leer",
            "Me encanta",
            "Ayudar a otros",
            "Liderazgo",
            "Educación",
            "Escuela",
            "Perfil de prueba - Ingeniería de Sistemas recomendada",
            datetime.now().strftime("%Y-%m-%d")
        ]
        
        # Verificar que no haya datos duplicados de prueba
        existing_data = sheets.sheet.get_all_values()
        if len(existing_data) <= 1:  # Solo encabezados
            sheets.sheet.append_row(test_data)
            print("✅ Datos de prueba agregados")
        else:
            print("ℹ️ La hoja ya contiene datos")
        
        print("✅ Configuración de Google Sheets completada")
        return True
        
    except Exception as e:
        print(f"❌ Error configurando Google Sheets: {str(e)}")
        return False

if __name__ == "__main__":
    setup_sheets()