import unittest
import json
import os
from datetime import datetime, timedelta
from utils.session_manager import SessionManager

class TestSessionManager(unittest.TestCase):
    def setUp(self):
        """Configuración antes de cada prueba"""
        self.session_manager = SessionManager(session_timeout_minutes=1)
        self.test_user = "whatsapp:+51999999999"
    
    def tearDown(self):
        """Limpieza después de cada prueba"""
        if os.path.exists('test_sessions.json'):
            os.remove('test_sessions.json')
    
    def test_new_session(self):
        """Prueba crear una nueva sesión"""
        session = self.session_manager.get_session(self.test_user)
        self.assertEqual(session['state'], 'idle')
        self.assertEqual(session['current_question'], 0)
        self.assertEqual(session['answers'], {})
    
    def test_update_session(self):
        """Prueba actualizar una sesión"""
        session = self.session_manager.get_session(self.test_user)
        session['state'] = 'active'
        session['answers']['question_1'] = 'Matemáticas'
        self.session_manager.save_session(self.test_user, session)
        
        updated_session = self.session_manager.get_session(self.test_user)
        self.assertEqual(updated_session['state'], 'active')
        self.assertEqual(updated_session['answers']['question_1'], 'Matemáticas')
    
    def test_session_timeout(self):
        """Prueba expiración de sesión"""
        session = self.session_manager.get_session(self.test_user)
        session['last_activity'] = (datetime.now() - timedelta(minutes=5)).isoformat()
        self.session_manager.save_session(self.test_user, session)
        
        self.session_manager.clean_expired_sessions()
        self.assertNotIn(self.test_user, self.session_manager.sessions)
    
    def test_get_stats(self):
        """Prueba estadísticas de sesión"""
        # Crear varias sesiones
        user1 = "whatsapp:+51999999991"
        user2 = "whatsapp:+51999999992"
        
        session1 = self.session_manager.get_session(user1)
        session1['state'] = 'active'
        self.session_manager.save_session(user1, session1)
        
        session2 = self.session_manager.get_session(user2)
        session2['state'] = 'completed'
        self.session_manager.save_session(user2, session2)
        
        stats = self.session_manager.get_stats()
        self.assertGreaterEqual(stats['total_sessions'], 2)
        self.assertGreaterEqual(stats['active_sessions'], 1)
        self.assertGreaterEqual(stats['completed_sessions'], 1)

if __name__ == '__main__':
    unittest.main()