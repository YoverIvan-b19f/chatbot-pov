# VocalIA - Chatbot de Orientación Vocacional

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![OpenAI](https://img.shields.io/badge/openai-1.6.1-orange.svg)](https://openai.com/)
[![Twilio](https://img.shields.io/badge/twilio-8.10.0-red.svg)](https://www.twilio.com/)

## 📋 Descripción

VocalIA es un chatbot de orientación vocacional diseñado para estudiantes de 5to de secundaria de colegios públicos de Cajamarca. El sistema guía a los estudiantes a través de 8 preguntas sobre sus intereses y habilidades, generando un perfil vocacional personalizado con carreras recomendadas, instituciones disponibles y vías de acceso.

## 🚀 Características

- ✅ Conversación natural con IA (OpenAI GPT-3.5)
- ✅ Integración con WhatsApp (Twilio)
- ✅ Almacenamiento anonimizado en Google Sheets
- ✅ Manejo de sesiones multi-usuario
- ✅ Respuestas personalizadas en tiempo real
- ✅ Sistema de métricas y monitoreo

## 📦 Instalación

### Requisitos previos
- Python 3.10 o superior
- Cuenta en Twilio (WhatsApp Business API)
- Cuenta en OpenAI (API Key)
- Cuenta en Google Cloud (Sheets API)
- ngrok (para pruebas locales)

### Pasos de instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/tu-usuario/chatbot-pov.git
cd chatbot-pov