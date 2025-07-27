import sqlite3
import os
from contextlib import contextmanager

# Database path
DB_PATH = os.environ.get('DATABASE_URL', '/tmp/earnchain.db') if os.environ.get('RENDER') else 'earnchain.db'

def init_db():
    """Initialize the database with tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            balance REAL DEFAULT 0,
            created_at INTEGER DEFAULT (strftime('%s', 'now'))
        )
    ''')
    
    # Create ads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            reward REAL NOT NULL DEFAULT 0.01,
            created_at INTEGER DEFAULT (strftime('%s', 'now'))
        )
    ''')
    
    # Create clicks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            ad_id INTEGER NOT NULL,
            points REAL DEFAULT 0,
            timestamp INTEGER DEFAULT (strftime('%s', 'now')),
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (ad_id) REFERENCES ads (id)
        )
    ''')
    
    # Insert sample ads
    cursor.execute('DELETE FROM ads')
    sample_ads = [
        ('🎮 Premium Game Access', 'https://example.com/game1', 0.02),
        ('🛍️ Exclusive Shopping Deal', 'https://example.com/shop1', 0.03),
        ('🎬 Movie Streaming Offer', 'https://example.com/movie1', 0.015),
        ('🎵 Music Premium Trial', 'https://example.com/music1', 0.01),
        ('📚 Online Course Discount', 'https://example.com/course1', 0.025)
    ]
    
    cursor.executemany('INSERT INTO ads (title, url, reward) VALUES (?, ?, ?)', sample_ads)
    
    conn.commit()
    conn.close()

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()