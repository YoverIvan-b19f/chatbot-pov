import os

def load_prompt(filename):
    """Carga un prompt desde un archivo"""
    prompt_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(prompt_dir, filename)
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"⚠️ Archivo de prompt no encontrado: {filename}")
        return ""

# Cargar prompts
SYSTEM_PROMPT = load_prompt('system_prompt.txt')
PROFILE_GENERATOR = load_prompt('profile_generator.txt')

# Preguntas del cuestionario
QUESTIONS = [
    {
        "id": 1,
        "question": "📚 ¿Cuál es tu materia favorita en el colegio?",
        "options": ["Matemáticas", "Comunicación", "Ciencias", "Historia", "Arte o Música"],
        "options_text": "A) Matemáticas\nB) Comunicación\nC) Ciencias\nD) Historia\nE) Arte o Música"
    },
    {
        "id": 2,
        "question": "💪 ¿En qué actividad te sientes más hábil?",
        "options": ["Resolver problemas", "Escribir o hablar", "Experimentar", "Organizar", "Crear cosas"],
        "options_text": "A) Resolver problemas\nB) Escribir o hablar\nC) Experimentar\nD) Organizar\nE) Crear cosas"
    },
    {
        "id": 3,
        "question": "⏰ ¿Qué haces en tu tiempo libre?",
        "options": ["Jugar videojuegos", "Leer", "Hacer deporte", "Ver videos/tutoriales", "Crear contenido"],
        "options_text": "A) Jugar videojuegos\nB) Leer\nC) Hacer deporte\nD) Ver videos/tutoriales\nE) Crear contenido"
    },
    {
        "id": 4,
        "question": "🤝 ¿Cómo te sientes trabajando en equipo?",
        "options": ["Me encanta", "Prefiero trabajar solo", "Depende del equipo", "No me gusta"],
        "options_text": "A) Me encanta\nB) Prefiero trabajar solo\nC) Depende del equipo\nD) No me gusta"
    },
    {
        "id": 5,
        "question": "🎯 ¿Qué tipo de trabajo te gustaría tener en el futuro?",
        "options": ["Ayudar a otros", "Crear tecnología", "Trabajar con números", "Expresar ideas", "Trabajar al aire libre"],
        "options_text": "A) Ayudar a otros\nB) Crear tecnología\nC) Trabajar con números\nD) Expresar ideas\nE) Trabajar al aire libre"
    },
    {
        "id": 6,
        "question": "🧠 ¿Qué habilidad te gustaría desarrollar más?",
        "options": ["Liderazgo", "Creatividad", "Razonamiento lógico", "Comunicación", "Trabajo en equipo"],
        "options_text": "A) Liderazgo\nB) Creatividad\nC) Razonamiento lógico\nD) Comunicación\nE) Trabajo en equipo"
    },
    {
        "id": 7,
        "question": "🏥 ¿Qué problema te gustaría resolver en tu comunidad?",
        "options": ["Salud", "Educación", "Medio ambiente", "Tecnología", "Economía"],
        "options_text": "A) Salud\nB) Educación\nC) Medio ambiente\nD) Tecnología\nE) Economía"
    },
    {
        "id": 8,
        "question": "💼 ¿Qué tipo de entorno laboral prefieres?",
        "options": ["Oficina", "Campo", "Hospital/Laboratorio", "Escuela", "Empresa de tecnología"],
        "options_text": "A) Oficina\nB) Campo\nC) Hospital/Laboratorio\nD) Escuela\nE) Empresa de tecnología"
    }
]