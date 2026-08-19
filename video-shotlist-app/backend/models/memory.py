import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
import chromadb
from chromadb.config import Settings


class MemoryService:
    """Service for session memory and vector storage"""
    
    def __init__(self, db_path: str = "sessions.db", chroma_path: str = "chroma_db"):
        self.db_path = db_path
        self._init_sqlite()
        self._init_chroma(chroma_path)
    
    def _init_sqlite(self):
        """Initialize SQLite database for session storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                video_path TEXT,
                status TEXT,
                data TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        """)
        
        # Prompts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prompts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                type TEXT,
                content TEXT,
                created_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _init_chroma(self, chroma_path: str):
        """Initialize ChromaDB for vector storage"""
        os.makedirs(chroma_path, exist_ok=True)
        self.chroma_client = chromadb.PersistentClient(path=chroma_path)
        self.shotlist_collection = self.chroma_client.get_or_create_collection(
            name="shotlists",
            metadata={"description": "Vector embeddings of shotlist descriptions"}
        )
    
    def save_session(self, session_data: Dict[str, Any]):
        """Save or update a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO sessions (session_id, video_path, status, data, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session_data["session_id"],
            session_data.get("video_path"),
            session_data.get("status", "pending"),
            json.dumps(session_data),
            session_data.get("created_at", datetime.now().isoformat()),
            session_data.get("updated_at", datetime.now().isoformat()),
        ))
        
        conn.commit()
        conn.close()
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a session by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT data FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            return json.loads(row[0])
        return None
    
    def update_session(self, session_id: str, updates: Dict[str, Any]):
        """Update specific fields in a session"""
        session = self.get_session(session_id)
        if session:
            session.update(updates)
            session["updated_at"] = datetime.now().isoformat()
            self.save_session(session)
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT data FROM sessions ORDER BY updated_at DESC")
        rows = cursor.fetchall()
        
        conn.close()
        
        return [json.loads(row[0]) for row in rows]
    
    def delete_session(self, session_id: str):
        """Delete a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        
        # Also remove from ChromaDB
        try:
            self.shotlist_collection.delete(where={"session_id": session_id})
        except Exception:
            pass
        
        conn.commit()
        conn.close()
    
    def store_shotlist_embeddings(self, session_id: str, shotlist: List[Dict[str, Any]]):
        """Store shotlist embeddings in ChromaDB for semantic search"""
        if not shotlist:
            return
        
        documents = []
        metadatas = []
        ids = []
        
        for i, shot in enumerate(shotlist):
            # Create document from shot description
            doc_parts = [
                shot.get("description", ""),
                shot.get("shot_type", ""),
                shot.get("camera_angle", ""),
                shot.get("camera_movement", ""),
                shot.get("lighting", ""),
                shot.get("mood_tone", ""),
            ]
            document = " ".join(filter(None, doc_parts))
            
            if document:
                documents.append(document)
                metadatas.append({
                    "session_id": session_id,
                    "shot_number": shot.get("shot_number", i),
                    "time_start": str(shot.get("time_start", 0)),
                    "time_end": str(shot.get("time_end", 0)),
                })
                ids.append(f"{session_id}_shot_{i}")
        
        if documents:
            self.shotlist_collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
    
    def search_similar_shots(self, query: str, n_results: int = 5, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for similar shots using semantic similarity"""
        where_clause = None
        if session_id:
            where_clause = {"session_id": session_id}
        
        results = self.shotlist_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause,
        )
        
        formatted_results = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "document": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None,
                })
        
        return formatted_results
    
    def save_prompt(self, prompt_data: Dict[str, Any]):
        """Save a custom prompt"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO prompts (name, type, content, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            prompt_data["name"],
            prompt_data["type"],
            prompt_data["content"],
            prompt_data.get("created_at", datetime.now().isoformat()),
        ))
        
        conn.commit()
        conn.close()
    
    def list_prompts(self) -> List[Dict[str, Any]]:
        """List all custom prompts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, type, content, created_at FROM prompts ORDER BY created_at DESC")
        rows = cursor.fetchall()
        
        conn.close()
        
        return [
            {
                "name": row[0],
                "type": row[1],
                "content": row[2],
                "created_at": row[3],
            }
            for row in rows
        ]
    
    def delete_prompt(self, prompt_id: int):
        """Delete a custom prompt"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM prompts WHERE id = ?", (prompt_id,))
        conn.commit()
        conn.close()
