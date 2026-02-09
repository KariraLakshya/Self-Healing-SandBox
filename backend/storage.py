"""
Redis Storage Module
Handles persistent storage of session data, logs, and thought signatures.
"""

import os
import json
import redis
from dotenv import load_dotenv

load_dotenv()

# Redis Configuration
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

class RedisStorage:
    def __init__(self):
        try:
            self.client = redis.from_url(REDIS_URL, decode_responses=True)
            self.client.ping()
            print(f"✅ Connected to Redis at {REDIS_URL}")
            self.enabled = True
        except redis.ConnectionError:
            print("⚠️ Redis not available. Falling back to in-memory storage.")
            self.enabled = False
            self.memory_store = {}
            
    def save(self, session_id: str, data: dict):
        """Save initial session data."""
        if self.enabled:
            # Convert lists to JSON strings for Redis
            # But simpler to just store the whole session as one JSON blob for now
            self.client.set(f"session:{session_id}", json.dumps(data))
            # Also add to list of all sessions
            self.client.rpush("sessions", session_id)
        else:
            self.memory_store[session_id] = data

    def get(self, session_id: str) -> dict | None:
        """Retrieve session data."""
        if self.enabled:
            data = self.client.get(f"session:{session_id}")
            return json.loads(data) if data else None
        else:
            return self.memory_store.get(session_id)

    def update(self, session_id: str, updates: dict):
        """Update session fields."""
        current = self.get(session_id)
        if current:
            current.update(updates)
            self.save(session_id, current)

    def append_log(self, session_id: str, message: str):
        """Append a log message."""
        current = self.get(session_id)
        if current:
            if "logs" not in current:
                current["logs"] = []
            current["logs"].append(message)
            self.save(session_id, current)

    def append_thought(self, session_id: str, thought: str):
        """Append a thought signature."""
        current = self.get(session_id)
        if current:
            if "thoughts" not in current:
                current["thoughts"] = []
            current["thoughts"].append(thought)
            self.save(session_id, current)

    def list_all(self) -> list[dict]:
        """List all sessions."""
        if self.enabled:
            session_ids = self.client.lrange("sessions", 0, -1)
            sessions = []
            for sid in session_ids:
                data = self.get(sid)
                if data:
                    sessions.append(data)
            return sessions
        else:
            return list(self.memory_store.values())

    def get_thoughts(self, session_id: str) -> list[str]:
        """Get thoughts for a session."""
        data = self.get(session_id)
        return data.get("thoughts", []) if data else []

    def delete(self, session_id: str):
        """Delete a session."""
        if self.enabled:
            self.client.delete(f"session:{session_id}")
            self.client.lrem("sessions", 0, session_id)
        else:
            if session_id in self.memory_store:
                del self.memory_store[session_id]

# Singleton instance
store = RedisStorage()
