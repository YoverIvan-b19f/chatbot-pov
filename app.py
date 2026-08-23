import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

from config import config
from utils.session_manager import SessionManager
from utils.openai_helper import OpenAIHelper
from utils.sheets import GoogleSheetsHelper
from utils.validators import validate_phone_number, sanitize_input
from prompts import SYSTEM_PROMPT, QUESTIONS

# Configuración de logging
def setup_logging():
    log_dir = os.path.dirname(os.getenv('LOG_FILE', 'logs/app.log'))
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(os.getenv('LOG_FILE', 'logs/app.log')),
            logging.StreamHandler()
        ]
    )

setup_logging()
logger = logging.getLogger(__name__)

# Inicializar aplicación
app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'development')])

# Inicializar servicios
session_manager = SessionManager()
openai_helper = OpenAIHelper()
sheets_helper = GoogleSheetsHelper()

# Inicializar cliente Twilio para verificar webhook
twilio_client = Client(
    app.config['TWILIO_ACCOUNT_SID'],
    app.config['TWILIO_AUTH_TOKEN']
)

# Estados de la conversación
STATE_IDLE = 'idle'
STATE_ACTIVE = 'active'
STATE_COMPLETED = 'completed'
STATE_ERROR = 'error'

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint principal para mensajes de WhatsApp"""
    try:
        # Validar que la solicitud viene de Twilio
        # En producción, verificar firmas de Twilio
        
        # Obtener datos del mensaje
        incoming_msg = request.form.get('Body', '').strip()
        sender = request.form.get('From', '')
        
        # Validar entrada
        if not sender or not incoming_msg:
            return create_error_response("Mensaje inválido")
        
        # Sanitizar entrada del usuario
        incoming_msg = sanitize_input(incoming_msg)
        
        # Obtener ID anonimizado (últimos 4 dígitos del teléfono)
        anonymized_id = sender[-4:] if sender else '0000'
        
        logger.info(f"📱 Mensaje de {anonymized_id}: {incoming_msg[:50]}...")
        
        # Obtener o crear sesión
        session = session_manager.get_session(sender)
        
        # Manejar comandos especiales
        if incoming_msg in ['AYUDA', 'HELP', '?']:
            return handle_help(sender)
        
        if incoming_msg in ['REINICIAR', 'RESET', 'RESTART']:
            return handle_reset(sender)
        
        if incoming_msg in ['ESTADO', 'STATUS']:
            return handle_status(sender)
        
        # Lógica principal según estado
        if session['state'] == STATE_IDLE:
            if incoming_msg in ['HOLA', 'INICIAR', 'START', 'HOLI', 'COMENZAR']:
                return handle_start(sender, anonymized_id)
            else:
                return create_welcome_response()
        
        elif session['state'] == STATE_ACTIVE:
            return handle_question_response(sender, incoming_msg, anonymized_id)
        
        elif session['state'] == STATE_COMPLETED:
            return handle_completion(sender, anonymized_id)
        
        elif session['state'] == STATE_ERROR:
            return handle_error_recovery(sender)
        
        else:
            # Estado desconocido - resetear
            session_manager.reset_session(sender)
            return create_welcome_response()
            
    except Exception as e:
        logger.error(f"❌ Error en webhook: {str(e)}", exc_info=True)
        return create_error_response("⚠️ Lo siento, hubo un error. Por favor, intenta de nuevo enviando 'HOLA'")

def create_welcome_response():
    """Crea respuesta de bienvenida"""
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("""
👋 ¡Hola! Soy VocalIA, tu orientador vocacional.

🎯 Estoy aquí para ayudarte a descubrir qué carrera podría ser ideal para ti.

📝 Para comenzar, envía 'HOLA' y te haré 8 preguntas sobre tus intereses.

💡 También puedes enviar:
• AYUDA - Ver opciones disponibles
• REINICIAR - Comenzar de nuevo
    """)
    return str(resp)

def handle_help(sender):
    """Maneja el comando de ayuda"""
    session = session_manager.get_session(sender)
    resp = MessagingResponse()
    msg = resp.message()
    
    help_text = """
📚 **AYUDA - Comandos disponibles:**

• **HOLA** - Iniciar el test vocacional
• **REINICIAR** - Comenzar el test desde cero
• **ESTADO** - Ver tu progreso actual
• **AYUDA** - Mostrar este mensaje

🎯 **Sobre el test:**
Responderás 8 preguntas sobre tus intereses y habilidades.
Al finalizar, recibirás un perfil con carreras recomendadas.

⏱️ Tiempo estimado: 5-10 minutos
    """
    
    if session['state'] == STATE_ACTIVE:
        current_q = session.get('current_question', 0)
        total_q = len(QUESTIONS)
        help_text += f"\n📊 Vas en la pregunta {current_q + 1} de {total_q}"
    
    msg.body(help_text)
    return str(resp)

def handle_reset(sender):
    """Reinicia la sesión del usuario"""
    session_manager.reset_session(sender)
    resp = MessagingResponse()
    msg = resp.message()
    msg.body("🔄 ¡Listo! He reiniciado tu progreso. Envía 'HOLA' para comenzar de nuevo.")
    return str(resp)

def handle_status(sender):
    """Muestra el estado actual de la sesión"""
    session = session_manager.get_session(sender)
    resp = MessagingResponse()
    msg = resp.message()
    
    if session['state'] == STATE_IDLE:
        msg.body("📌 No tienes una sesión activa. Envía 'HOLA' para comenzar.")
    elif session['state'] == STATE_ACTIVE:
        current_q = session.get('current_question', 0)
        total_q = len(QUESTIONS)
        answered = len(session.get('answers', {}))
        msg.body(f"📊 Progreso: Pregunta {answered + 1} de {total_q}\n✅ Respondidas: {answered}")
    elif session['state'] == STATE_COMPLETED:
        msg.body("✅ ¡Ya completaste el test! Revisa tu perfil vocacional arriba.")
    else:
        msg.body("🔄 Estado desconocido. Envía 'REINICIAR' para comenzar de nuevo.")
    
    return str(resp)

def handle_start(sender, anonymized_id):
    """Inicia una nueva sesión de test"""
    session = session_manager.get_session(sender)
    
    # Resetear estado para nueva sesión
    session_manager.reset_session(sender)
    session = session_manager.get_session(sender)
    
    session['state'] = STATE_ACTIVE
    session['current_question'] = 0
    session['answers'] = {}
    session['start_time'] = datetime.now().isoformat()
    session_manager.save_session(sender, session)
    
    # Enviar primera pregunta
    first_question = QUESTIONS[0]
    resp = MessagingResponse()
    msg = resp.message()
    
    msg.body(f"""
🎯 ¡Excelente! Te haré {len(QUESTIONS)} preguntas para conocerte mejor.

📝 Responde con la letra de la opción que más te identifique.

{format_question(first_question)}
    """)
    
    return str(resp)

def handle_question_response(sender, response, anonymized_id):
    """Procesa la respuesta a una pregunta"""
    session = session_manager.get_session(sender)
    current_q = session.get('current_question', 0)
    
    # Validar respuesta
    if not validate_response(response, current_q):
        return send_question_again(sender, current_q)
    
    # Guardar respuesta
    answer_key = f'question_{current_q + 1}'
    session['answers'][answer_key] = response
    session_manager.save_session(sender, session)
    
    # Verificar si es la última pregunta
    if current_q + 1 >= len(QUESTIONS):
        return generate_profile(sender, anonymized_id)
    
    # Avanzar a la siguiente pregunta
    session['current_question'] = current_q + 1
    session_manager.save_session(sender, session)
    
    # Enviar siguiente pregunta
    next_question = QUESTIONS[current_q + 1]
    resp = MessagingResponse()
    msg = resp.message()
    
    progress = f"📊 Pregunta {current_q + 2} de {len(QUESTIONS)}"
    msg.body(f"{progress}\n\n{format_question(next_question)}")
    
    return str(resp)

def generate_profile(sender, anonymized_id):
    """Genera el perfil vocacional final usando OpenAI"""
    session = session_manager.get_session(sender)
    
    try:
        # Preparar respuestas para análisis
        answers_text = "\n".join([f"Pregunta {k}: {v}" for k, v in session['answers'].items()])
        
        # Generar perfil con OpenAI
        profile_text = openai_helper.generate_profile(
            answers=session['answers'],
            user_answers_text=answers_text
        )
        
        # Guardar en Google Sheets
        sheets_helper.save_profile(
            anonymized_id=anonymized_id,
            answers=session['answers'],
            profile=profile_text,
            timestamp=datetime.now()
        )
        
        # Actualizar estado
        session['state'] = STATE_COMPLETED
        session['profile'] = profile_text
        session['completion_time'] = datetime.now().isoformat()
        session_manager.save_session(sender, session)
        
        # Enviar perfil al usuario
        resp = MessagingResponse()
        msg = resp.message()
        
        msg.body(f"""
🎉 ¡Felicidades! Has completado el test vocacional.

📚 **Tu perfil vocacional:**

{profile_text}

📌 Puedes enviar:
• REINICIAR - Para hacer el test de nuevo
• AYUDA - Para ver más opciones

¡Éxito en tu camino educativo! 🚀
        """)
        
        return str(resp)
        
    except Exception as e:
        logger.error(f"❌ Error generando perfil: {str(e)}")
        
        # Intentar guardar al menos las respuestas
        try:
            sheets_helper.save_profile(
                anonymized_id=anonymized_id,
                answers=session['answers'],
                profile="ERROR: No se pudo generar el perfil",
                timestamp=datetime.now()
            )
        except:
            pass
        
        session['state'] = STATE_ERROR
        session_manager.save_session(sender, session)
        
        return create_error_response(
            "⚠️ Lo siento, hubo un error al generar tu perfil. "
            "Por favor, envía 'REINICIAR' para intentar de nuevo."
        )

def handle_completion(sender, anonymized_id):
    """Maneja usuarios que ya completaron el test"""
    session = session_manager.get_session(sender)
    resp = MessagingResponse()
    msg = resp.message()
    
    if 'profile' in session:
        msg.body(f"""
📚 Ya tienes tu perfil vocacional listo.

{format_profile_preview(session['profile'])}

🔄 Para hacer el test de nuevo, envía 'REINICIAR'
❓ Para más ayuda, envía 'AYUDA'
        """)
    else:
        msg.body("👋 ¡Hola de nuevo! Para obtener tu perfil vocacional, envía 'HOLA' para comenzar el test.")
    
    return str(resp)

def handle_error_recovery(sender):
    """Recupera sesiones en estado de error"""
    session = session_manager.get_session(sender)
    resp = MessagingResponse()
    msg = resp.message()
    
    msg.body("""
⚠️ Tu sesión anterior tuvo un error.

Por favor, elige una opción:
• REINICIAR - Comenzar de nuevo
• AYUDA - Ver opciones disponibles
• HOLA - Intentar continuar
    """)
    
    return str(resp)

def send_question_again(sender, question_index):
    """Reenvía una pregunta porque la respuesta fue inválida"""
    question = QUESTIONS[question_index]
    resp = MessagingResponse()
    msg = resp.message()
    
    msg.body(f"""
⚠️ Por favor, responde con una opción válida (A, B, C, D o E).

{format_question(question)}
    """)
    
    return str(resp)

def format_question(question):
    """Formatea una pregunta para enviar por WhatsApp"""
    return f"{question['question']}\n\n{question['options_text']}"

def format_profile_preview(profile_text):
    """Formatea un preview del perfil"""
    lines = profile_text.split('\n')[:5]
    return '\n'.join(lines) + "\n\n..."

def validate_response(response, question_index):
    """Valida que la respuesta sea válida"""
    if not response:
        return False
    
    # Validar que sea una opción válida (A, B, C, D, E)
    valid_options = ['A', 'B', 'C', 'D', 'E']
    response_clean = response.strip().upper()
    
    # Aceptar solo letras simples
    if response_clean in valid_options:
        return True
    
    # También aceptar respuestas que contengan la opción
    for option in valid_options:
        if option in response_clean:
            return True
    
    return False

def create_error_response(message):
    """Crea una respuesta de error"""
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(message)
    return str(resp)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Verificar conexiones
        services_status = {
            'twilio': bool(app.config['TWILIO_ACCOUNT_SID']),
            'openai': bool(app.config['OPENAI_API_KEY']),
            'google_sheets': sheets_helper.sheet is not None,
            'session_manager': bool(session_manager)
        }
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': app.config.get('APP_VERSION', '1.0.0'),
            'services': services_status,
            'active_sessions': len(session_manager.sessions)
        }), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Endpoint para estadísticas"""
    try:
        session_stats = session_manager.get_stats()
        sheets_stats = sheets_helper.get_stats() if sheets_helper.sheet else None
        
        return jsonify({
            'session_stats': session_stats,
            'sheets_stats': sheets_stats,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    try:
        # Validar configuración
        app.config.validate()
        logger.info(f"🚀 Iniciando {app.config['APP_NAME']} v{app.config['APP_VERSION']}")
        logger.info(f"📊 Entorno: {app.config['FLASK_ENV']}")
        
        app.run(
            host='0.0.0.0',
            port=app.config['PORT'],
            debug=app.config['FLASK_ENV'] == 'development'
        )
        
    except Exception as e:
        logger.error(f"❌ Error al iniciar: {str(e)}")
        exit(1)