import re
import logging

logger = logging.getLogger(__name__)

def validate_phone_number(phone_number):
    """
    Valida que el número de teléfono tenga formato correcto
    Ejemplo: whatsapp:+51999999999
    """
    if not phone_number:
        return False
    
    pattern = r'^whatsapp:\+\d{10,15}$'
    return bool(re.match(pattern, phone_number))

def sanitize_input(text):
    """
    Sanitiza la entrada del usuario
    - Elimina espacios extra
    - Convierte a mayúsculas para comandos
    - Limpia caracteres especiales
    """
    if not text:
        return ""
    
    # Eliminar espacios al inicio y final
    text = text.strip()
    
    # Si es un comando corto, convertir a mayúsculas
    if len(text) <= 10:
        text = text.upper()
    
    # Eliminar caracteres peligrosos
    text = re.sub(r'[<>{}\[\]\\]', '', text)
    
    # Limitar longitud
    return text[:500]

def validate_response(response, question_index=None):
    """
    Valida la respuesta del usuario
    """
    if not response:
        return False
    
    response = response.strip().upper()
    
    # Si es un comando especial
    if response in ['AYUDA', 'HELP', 'REINICIAR', 'RESET', 'ESTADO', 'STATUS']:
        return True
    
    # Para preguntas con opciones (A, B, C, D, E)
    if question_index is not None:
        valid_options = ['A', 'B', 'C', 'D', 'E']
        
        # Aceptar solo letras
        if response in valid_options:
            return True
        
        # Aceptar respuestas que contengan la letra
        for option in valid_options:
            if option in response:
                return True
    
    # Para respuestas libres (no aplica por ahora)
    return True

def extract_option(response):
    """
    Extrae la opción seleccionada de una respuesta
    """
    if not response:
        return None
    
    response = response.strip().upper()
    
    # Si es una letra solita
    if response in ['A', 'B', 'C', 'D', 'E']:
        return response
    
    # Buscar la letra en la respuesta
    for option in ['A', 'B', 'C', 'D', 'E']:
        if option in response:
            return option
    
    return None

def format_phone_number(phone):
    """
    Formatea el número de teléfono para mostrar
    """
    if not phone:
        return "0000"
    
    # Si es de WhatsApp, extraer solo el número
    if phone.startswith('whatsapp:'):
        phone = phone.replace('whatsapp:', '')
    
    # Retornar últimos 4 dígitos
    return phone[-4:] if len(phone) >= 4 else phone.zfill(4)