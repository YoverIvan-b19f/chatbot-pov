import json
import os
from datetime import datetime, timedelta
from collections import defaultdict

class SessionManager:
    def __init__(self, session_timeout_minutes=30):
        self.sessions = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self.sessions_file = 'sessions.json'
        self.load_sessions()
    
    def get_session(self, user_id):
        """Get or create a session for a user"""
        self.clean_expired_sessions()
        
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                'state': 'idle',  # idle, active, completed
                'current_question': 0,
                'answers': {},
                'start_time': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat()
            }
            self.save_sessions()
        
        # Update last activity
        self.sessions[user_id]['last_activity'] = datetime.now().isoformat()
        self.save_sessions()
        
        return self.sessions[user_id]
    
    def save_session(self, user_id, session_data):
        """Save session data"""
        session_data['last_activity'] = datetime.now().isoformat()
        self.sessions[user_id] = session_data
        self.save_sessions()
    
    def clean_expired_sessions(self):
        """Remove expired sessions"""
        current_time = datetime.now()
        expired_users = []
        
        for user_id, session in self.sessions.items():
            last_activity = datetime.fromisoformat(session['last_activity'])
            if current_time - last_activity > self.session_timeout:
                expired_users.append(user_id)
        
        for user_id in expired_users:
            del self.sessions[user_id]
        
        if expired_users:
            self.save_sessions()
    
    def get_stats(self):
        """Get session statistics"""
        stats = {
            'total_sessions': len(self.sessions),
            'active_sessions': 0,
            'completed_sessions': 0,
            'completion_rate': 0
        }
        
        for session in self.sessions.values():
            if session['state'] == 'active':
                stats['active_sessions'] += 1
            elif session['state'] == 'completed':
                stats['completed_sessions'] += 1
        
        if stats['total_sessions'] > 0:
            stats['completion_rate'] = (stats['completed_sessions'] / stats['total_sessions']) * 100
        
        return stats
    
    def load_sessions(self):
        """Load sessions from file"""
        if os.path.exists(self.sessions_file):
            try:
                with open(self.sessions_file, 'r') as f:
                    self.sessions = json.load(f)
            except:
                self.sessions = {}
    
    def save_sessions(self):
        """Save sessions to file"""
        try:
            with open(self.sessions_file, 'w') as f:
                json.dump(self.sessions, f)
        except Exception as e:
            print(f"Error saving sessions: {e}")
    
    def reset_session(self, user_id):
        """Reset a user's session"""
        if user_id in self.sessions:
            del self.sessions[user_id]
            self.save_sessions()