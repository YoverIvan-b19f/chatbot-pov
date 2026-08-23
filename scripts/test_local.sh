#!/bin/bash
# Script para probar el sistema localmente

echo "🧪 Probando VocalIA - Chatbot de Orientación Vocacional"
echo "======================================================"

# Verificar entorno virtual
if [ ! -d "venv" ]; then
    echo "❌ Entorno virtual no encontrado. Ejecuta: python -m venv venv"
    exit 1
fi

# Activar entorno virtual
source venv/bin/activate

# Verificar dependencias
echo "📦 Verificando dependencias..."
pip install -r requirements.txt

# Verificar archivo .env
if [ ! -f ".env" ]; then
    echo "⚠️ Archivo .env no encontrado"
    echo "Copia .env.example a .env y configura tus credenciales"
    exit 1
fi

# Verificar credenciales de Google Sheets
if [ ! -f "credentials.json" ]; then
    echo "⚠️ credentials.json no encontrado"
    echo "Descarga tu archivo de credenciales de Google Cloud Console"
fi

# Verificar estructura de directorios
echo "📁 Verificando estructura de directorios..."
mkdir -p logs
mkdir -p data

# Configurar Google Sheets
echo "📊 Configurando Google Sheets..."
python scripts/setup_google_sheets.py

# Ejecutar pruebas
echo "🧪 Ejecutando pruebas..."
python -m pytest tests/ -v --tb=short

# Iniciar servidor
echo "🚀 Iniciando servidor..."
python app.py

# Nota: El servidor se ejecutará en http://localhost:5000
echo ""
echo "✅ Servidor iniciado en http://localhost:5000"
echo "📱 Configura tu webhook de Twilio con: ngrok http 5000"