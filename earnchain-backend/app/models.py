from app.database import get_db
import time

class User:
    @staticmethod
    def register(user_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO users (id, balance) VALUES (?, 0)', (user_id,))
            conn.commit()
    
    @staticmethod
    def get_balance(user_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT balance FROM users WHERE id = ?', (user_id,))
            row = cursor.fetchone()
            return row['balance'] if row else 0

class Ad:
    @staticmethod
    def get_available_ads(user_id):
        with get_db() as conn:
            cursor = conn.cursor()
            now = int(time.time())
            twenty_four_hours_ago = now - (24 * 60 * 60)
            
            cursor.execute('''
                SELECT a.id, a.title, a.url, a.reward
                FROM ads a
                LEFT JOIN clicks c ON c.ad_id = a.id 
                  AND c.user_id = ? 
                  AND c.timestamp > ?
                WHERE c.ad_id IS NULL
                ORDER BY a.id
            ''', (user_id, twenty_four_hours_ago))
            
            return [dict(row) for row in cursor.fetchall()]
    
    @staticmethod
    def get_ad(ad_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT reward FROM ads WHERE id = ?', (ad_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

class Click:
    @staticmethod
    def record_click(user_id, ad_id, points):
        with get_db() as conn:
            cursor = conn.cursor()
            now = int(time.time())
            
            # Check if already clicked in last 24 hours
            twenty_four_hours_ago = now - (24 * 60 * 60)
            cursor.execute('''
                SELECT id FROM clicks 
                WHERE user_id = ? AND ad_id = ? AND timestamp > ?
            ''', (user_id, ad_id, twenty_four_hours_ago))
            
            if cursor.fetchone():
                return False  # Already clicked
            
            # Record click and update balance
            cursor.execute('''
                INSERT INTO clicks (user_id, ad_id, points, timestamp) 
                VALUES (?, ?, ?, ?)
            ''', (user_id, ad_id, points, now))
            
            cursor.execute('''
                UPDATE users SET balance = balance + ? WHERE id = ?
            ''', (points, user_id))
            
            conn.commit()
            return True
    
    @staticmethod
    def get_history(user_id):
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT a.title, c.points, c.timestamp
                FROM clicks c
                JOIN ads a ON c.ad_id = a.id
                WHERE c.user_id = ?
                ORDER BY c.timestamp DESC
                LIMIT 20
            ''', (user_id,))
            
            return [dict(row) for row in cursor.fetchall()]