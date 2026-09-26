import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any

class DatabaseManager:
    def __init__(self):
        self.db_file = "interview_data.db"
        self._create_tables()
        
    def _create_tables(self):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        # Users table
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     username TEXT UNIQUE,
                     created_at TIMESTAMP)''')
                     
        # Interviews table
        c.execute('''CREATE TABLE IF NOT EXISTS interviews
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id INTEGER,
                     job_role TEXT,
                     question TEXT,
                     answer TEXT,
                     feedback TEXT,
                     score FLOAT,
                     category TEXT,
                     date TIMESTAMP,
                     FOREIGN KEY (user_id) REFERENCES users(id))''')
        
        # Interview analysis table
        c.execute('''CREATE TABLE IF NOT EXISTS interview_analysis
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     interview_id INTEGER,
                     response_quality FLOAT,
                     technical_accuracy FLOAT,
                     communication_clarity FLOAT,
                     timestamp TIMESTAMP,
                     FOREIGN KEY (interview_id) REFERENCES interviews(id))''')

        # Interview metrics table (per-metric rows)
        c.execute('''CREATE TABLE IF NOT EXISTS interview_metrics
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     interview_id INTEGER,
                     metric_type TEXT,
                     metric_value FLOAT,
                     timestamp TIMESTAMP,
                     FOREIGN KEY (interview_id) REFERENCES interviews(id))''')

        # Performance analytics table
        c.execute('''CREATE TABLE IF NOT EXISTS performance_analytics
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     interview_id INTEGER,
                     attention_score FLOAT,
                     eye_contact_score FLOAT,
                     speech_clarity_score FLOAT,
                     confidence_score FLOAT,
                     body_language_score FLOAT,
                     timestamp TIMESTAMP,
                     FOREIGN KEY (interview_id) REFERENCES interviews(id))''')

        conn.commit()
        conn.close()
        
    def add_user(self, username):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, created_at) VALUES (?, ?)",
                     (username, datetime.now()))
            user_id = c.lastrowid
            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            c.execute("SELECT id FROM users WHERE username = ?", (username,))
            return c.fetchone()[0]
        finally:
            conn.close()
            
    def save_interview(self, user_id, job_role, question, answer, feedback, score,
                      category=None):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("""INSERT INTO interviews 
                    (user_id, job_role, question, answer, feedback, score,
                     category, date)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                 (user_id, job_role, question, answer, feedback, score,
                  category, datetime.now()))
        conn.commit()
        conn.close()
        
    def get_user_interviews(self, user_id):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("""SELECT * FROM interviews 
                    WHERE user_id = ? 
                    ORDER BY date DESC""", (user_id,))
        interviews = [dict(row) for row in c.fetchall()]
        conn.close()
        return interviews
        
    def get_user_statistics(self, user_id):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute("""SELECT 
                    COUNT(*) as total_interviews,
                    AVG(score) as avg_score,
                    COUNT(DISTINCT date(date)) as days_practiced
                    FROM interviews
                    WHERE user_id = ?""", (user_id,))
        stats = c.fetchone()
        conn.close()
        return {
            'total_interviews': stats[0],
            'avg_score': stats[1] or 0,
            'total_time': (stats[2] or 0) * 0.5  # Assuming 30min per day
        }
    
    def save_interview_metrics(self, interview_id: int, metrics: Dict[str, float]):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        timestamp = datetime.now()
        
        try:
            for metric_type, value in metrics.items():
                c.execute("""INSERT INTO interview_metrics 
                            (interview_id, metric_type, metric_value, timestamp)
                            VALUES (?, ?, ?, ?)""",
                         (interview_id, metric_type, value, timestamp))
            conn.commit()
        finally:
            conn.close()
    
    def save_performance_analytics(self, interview_id: int, analytics: Dict[str, float]):
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        try:
            c.execute("""INSERT INTO performance_analytics
                        (interview_id, attention_score, eye_contact_score,
                         speech_clarity_score, confidence_score, body_language_score,
                         timestamp)
                        VALUES (?, ?, ?, ?, ?, ?, ?)""",
                     (interview_id, analytics.get('attention', 0),
                      analytics.get('eye_contact', 0), analytics.get('speech_clarity', 0),
                      analytics.get('confidence', 0), analytics.get('body_language', 0),
                      datetime.now()))
            conn.commit()
        finally:
            conn.close()
    
    def get_performance_history(self, user_id: int, metric_type: str | None = None,
                              limit: int = 10) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        try:
            if metric_type:
                c.execute("""SELECT m.* FROM interview_metrics m
                            JOIN interviews i ON m.interview_id = i.id
                            WHERE i.user_id = ? AND m.metric_type = ?
                            ORDER BY m.timestamp DESC LIMIT ?""",
                         (user_id, metric_type, limit))
            else:
                c.execute("""SELECT p.* FROM performance_analytics p
                            JOIN interviews i ON p.interview_id = i.id
                            WHERE i.user_id = ?
                            ORDER BY p.timestamp DESC LIMIT ?""",
                         (user_id, limit))
            
            return [dict(row) for row in c.fetchall()]
        finally:
            conn.close()
    
    def get_performance_summary(self, user_id: int) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        
        try:
            c.execute("""SELECT 
                        AVG(attention_score) as avg_attention,
                        AVG(eye_contact_score) as avg_eye_contact,
                        AVG(speech_clarity_score) as avg_speech_clarity,
                        AVG(confidence_score) as avg_confidence,
                        AVG(body_language_score) as avg_body_language
                        FROM performance_analytics p
                        JOIN interviews i ON p.interview_id = i.id
                        WHERE i.user_id = ?
                        """, (user_id,))
            row = c.fetchone()
            
            return {
                'attention': row[0] or 0,
                'eye_contact': row[1] or 0,
                'speech_clarity': row[2] or 0,
                'confidence': row[3] or 0,
                'body_language': row[4] or 0
            }
        finally:
            conn.close()

    def get_recent_interviews(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        try:
            c.execute("""SELECT * FROM interviews
                        WHERE user_id = ?
                        ORDER BY date DESC LIMIT ?""",
                     (user_id, limit))
            return [dict(row) for row in c.fetchall()]
        finally:
            conn.close()
