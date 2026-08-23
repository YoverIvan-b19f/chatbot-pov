import os
import openai
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class OpenAIHelper:
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key or self.api_key.startswith('sk-xxx'):
            logger.warning("OPENAI_API_KEY no configurada correctamente")
            self.api_key = None
        else:
            openai.api_key = self.api_key
        self.model = os.getenv('OPENAI_MODEL', "gpt-3.5-turbo")
    
    def generate_response(self, system_prompt, user_message):
        """Generate a response using OpenAI API"""
        if not self.api_key:
            return self.get_fallback_response()
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=float(os.getenv('OPENAI_TEMPERATURE', '0.7')),
                max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '800')),
                presence_penalty=0.6,
                frequency_penalty=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return self.get_fallback_response()
    
    def generate_profile(self, answers, user_answers_text=None):
        """Generate a vocational profile from answers"""
        if not user_answers_text:
            user_answers_text = "\n".join([f"Pregunta {k}: {v}" for k, v in answers.items()])
        
        # Si no hay API key, usar respuestas predefinidas
        if not self.api_key:
            return self.get_fallback_profile(answers)
        
        prompt = f"""
        Basado en las siguientes respuestas de un estudiante de 5to de secundaria de Cajamarca:
        
        {user_answers_text}
        
        Genera un perfil vocacional detallado con:
        1. 3 carreras recomendadas (con descripcion breve y por que son adecuadas)
        2. Instituciones disponibles en Cajamarca (UNC, UNACH, UPN, institutos tecnicos)
        3. Costos aproximados por semestre
        4. Vias de acceso disponibles (Beca 18, Pronabec, otras becas)
        
        Se especifico para el contexto de Cajamarca y usa un lenguaje motivador.
        """
        
        system_prompt = """Eres un orientador vocacional experto en el contexto de Cajamarca y las oportunidades educativas en el Peru. 
        Tus respuestas deben ser claras, utiles y motivadoras para estudiantes de 5to de secundaria."""
        
        return self.generate_response(system_prompt, prompt)
    
    def get_fallback_response(self):
        """Respuesta de respaldo cuando OpenAI no esta disponible"""
        return """
        Gracias por compartir tus intereses. 

        Basado en tus respuestas, te recomiendo explorar carreras en:
        
        1. Ingenieria de Sistemas - Si te gusta la tecnologia y resolver problemas
        2. Educacion - Si te apasiona ensenar y ayudar a otros
        3. Administracion - Si te interesa la gestion y el liderazgo
        
        En Cajamarca puedes estudiar en:
        - Universidad Nacional de Cajamarca (UNC)
        - Universidad Privada del Norte (UPN)
        - Instituto Tecnologico de Cajamarca
        
        Para mas informacion sobre becas, consulta la pagina de PRONABEC.
        """
    
    def get_fallback_profile(self, answers):
        """Perfil de respaldo sin OpenAI"""
        return """
        PERFIL VOCACIONAL (Modo de Prueba)
        
        Basado en tus respuestas, te recomendamos:
        
        1. Ingenieria de Sistemas
           Duracion: 5 anos
           Instituciones: UNC, UPN
           Por que: Tu interes en tecnologia y solucion de problemas
        
        2. Educacion
           Duracion: 5 anos  
           Instituciones: UNC, UNACH
           Por que: Tu interes en ayudar a otros y trabajar con personas
        
        3. Administracion
           Duracion: 5 anos
           Instituciones: UNC, UPN
           Por que: Tu interes en liderazgo y organizacion
        
        Vias de acceso:
        - Beca 18: Para estudiantes de bajos recursos con buen rendimiento
        - Pronabec: Becas parciales y completas
        
        Para mas informacion, contacta a la oficina de admision de cada institucion.
        """