import sqlite3
import os
import json
from datetime import datetime
import threading

class ThumbnailDatabase:
    def __init__(self, db_path="data/thumbnails.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._local = threading.local()
        # We'll create connections on-demand per thread
        self.create_tables()
        
    @property
    def conn(self):
        """Get a thread-local database connection"""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path)
        return self._local.conn
        
    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Table for storing generated thumbnails
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS thumbnails (
            id TEXT PRIMARY KEY,
            original_image_path TEXT,
            thumbnail_path TEXT,
            prompt TEXT,
            properties TEXT,
            created_at TIMESTAMP
        )
        ''')
        
        # Table for storing user feedback
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thumbnail_id TEXT,
            rating INTEGER,
            feedback_text TEXT,
            created_at TIMESTAMP,
            FOREIGN KEY (thumbnail_id) REFERENCES thumbnails (id)
        )
        ''')
        
        self.conn.commit()
    
    def save_thumbnail(self, thumbnail_id, original_path, thumbnail_path, prompt, properties):
        """Save information about a generated thumbnail"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO thumbnails VALUES (?, ?, ?, ?, ?, ?)",
            (
                thumbnail_id,
                original_path,
                thumbnail_path,
                prompt,
                json.dumps(properties),
                datetime.now().isoformat()
            )
        )
        self.conn.commit()
    
    def save_feedback(self, thumbnail_id, rating, feedback_text):
        """Save user feedback about a thumbnail"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO feedback (thumbnail_id, rating, feedback_text, created_at) VALUES (?, ?, ?, ?)",
            (thumbnail_id, rating, feedback_text, datetime.now().isoformat())
        )
        self.conn.commit()
        
    def get_highly_rated_thumbnails(self, min_rating=4, limit=100):
        """Get thumbnails with high ratings for model training"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT t.thumbnail_path, t.properties, t.prompt 
            FROM thumbnails t 
            JOIN feedback f ON t.id = f.thumbnail_id 
            WHERE f.rating >= ? 
            GROUP BY t.id 
            ORDER BY AVG(f.rating) DESC 
            LIMIT ?
        ''', (min_rating, limit))
        
        results = []
        for row in cursor.fetchall():
            thumbnail_path, properties_json, prompt = row
            results.append({
                'thumbnail_path': thumbnail_path,
                'properties': json.loads(properties_json),
                'prompt': prompt
            })
        
        return results
    
    def close(self):
        """Close the database connection for the current thread"""
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
            del self._local.conn