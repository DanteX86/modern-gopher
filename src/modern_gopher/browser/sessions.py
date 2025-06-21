#!/usr/bin/env python3
"""
Session management for Modern Gopher browser.

This module handles saving and restoring browser sessions, including
current URL, browsing history, and browser state.
"""

import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


@dataclass
class BrowserSession:
    """Represents a saved browser session."""

    # Session metadata
    session_id: str
    name: str
    created_at: float
    last_used: float

    # Browser state
    current_url: str
    history: List[str]
    history_position: int
    selected_index: int

    # Search state
    is_searching: bool = False
    search_query: str = ""

    # Optional metadata
    description: str = ""
    tags: List[str] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.tags is None:
            self.tags = []

    @property
    def created_datetime(self) -> datetime:
        """Get creation time as datetime object."""
        return datetime.fromtimestamp(self.created_at)

    @property
    def last_used_datetime(self) -> datetime:
        """Get last used time as datetime object."""
        return datetime.fromtimestamp(self.last_used)

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BrowserSession":
        """Create session from dictionary."""
        return cls(**data)


class SessionManager:
    """Manages browser sessions for the Modern Gopher browser."""

    def __init__(self, session_file: str, backup_sessions: bool = True, max_sessions: int = 10):
        """
        Initialize session manager.

        Args:
            session_file: Path to the session file
            backup_sessions: Whether to create backup sessions
            max_sessions: Maximum number of sessions to keep
        """
        self.session_file = Path(session_file)
        self.backup_sessions = backup_sessions
        self.max_sessions = max_sessions

        # Ensure session directory exists
        self.session_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing sessions
        self.sessions: Dict[str, BrowserSession] = self._load_sessions()

    def _load_sessions(self) -> Dict[str, BrowserSession]:
        """Load sessions from file."""
        if not self.session_file.exists():
            logger.info(f"No session file found at {self.session_file}")
            return {}

        try:
            with open(self.session_file, "r", encoding="utf-8") as f:
                sessions_data = json.load(f)

            sessions = {}
            for session_id, session_data in sessions_data.items():
                try:
                    sessions[session_id] = BrowserSession.from_dict(session_data)
                except Exception as e:
                    logger.warning(f"Failed to load session {session_id}: {e}")

            logger.info(
                f"Loaded {
                    len(sessions)} sessions from {
                    self.session_file}"
            )
            return sessions

        except Exception as e:
            logger.error(
                f"Failed to load sessions from {
                    self.session_file}: {e}"
            )
            return {}

    def _save_sessions(self) -> bool:
        """Save sessions to file."""
        try:
            sessions_data = {}
            for session_id, session in self.sessions.items():
                sessions_data[session_id] = session.to_dict()

            # Create backup if enabled
            if self.backup_sessions and self.session_file.exists():
                backup_path = self.session_file.with_suffix(".json.backup")
                try:
                    import shutil

                    shutil.copy2(self.session_file, backup_path)
                    logger.debug(f"Created session backup: {backup_path}")
                except Exception as e:
                    logger.warning(f"Failed to create session backup: {e}")

            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(sessions_data, f, indent=2, default=str)

            logger.debug(f"Saved {len(self.sessions)} sessions to {self.session_file}")
            return True

        except Exception as e:
            logger.error(
                f"Failed to save sessions to {
                    self.session_file}: {e}"
            )
            return False

    def save_session(
        self,
        browser_state: Dict[str, Any],
        session_name: Optional[str] = None,
        session_id: Optional[str] = None,
        description: str = "",
        tags: List[str] = None,
    ) -> str:
        """
        Save current browser state as a session.

        Args:
            browser_state: Dictionary containing browser state
            session_name: Name for the session (auto-generated if None)
            session_id: ID for the session (auto-generated if None)
            description: Optional description
            tags: Optional tags for categorization

        Returns:
            Session ID of the saved session
        """
        current_time = time.time()

        # Generate session ID if not provided
        if session_id is None:
            session_id = f"session_{int(current_time)}"

        # Generate session name if not provided
        if session_name is None:
            current_url = browser_state.get("current_url", "Unknown")
            session_name = f"Session {
                datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M')}"
            if current_url and current_url != "Unknown":
                # Extract hostname for session name
                try:
                    from urllib.parse import urlparse

                    parsed = urlparse(current_url)
                    hostname = parsed.hostname or "unknown"
                    session_name = f"{hostname} - {
                        datetime.fromtimestamp(current_time).strftime('%H:%M')}"
                except Exception as e:
                    logger.debug(f"Failed to parse URL for session name: {e}")

        # Create session object
        session = BrowserSession(
            session_id=session_id,
            name=session_name,
            created_at=current_time,
            last_used=current_time,
            current_url=browser_state.get("current_url", ""),
            history=browser_state.get("history", []),
            history_position=browser_state.get("history_position", -1),
            selected_index=browser_state.get("selected_index", 0),
            is_searching=browser_state.get("is_searching", False),
            search_query=browser_state.get("search_query", ""),
            description=description,
            tags=tags or [],
        )

        # Store session
        self.sessions[session_id] = session

        # Clean up old sessions if we exceed max_sessions
        self._cleanup_old_sessions()

        # Save to file
        if self._save_sessions():
            logger.info(f"Session '{session_name}' saved with ID: {session_id}")
            return session_id
        else:
            logger.error(f"Failed to save session '{session_name}'")
            return ""

    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a session and return browser state.

        Args:
            session_id: ID of the session to load

        Returns:
            Dictionary containing browser state, or None if session not found
        """
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found")
            return None

        session = self.sessions[session_id]

        # Update last used time
        session.last_used = time.time()
        self._save_sessions()

        # Return browser state
        browser_state = {
            "current_url": session.current_url,
            "history": session.history.copy(),
            "history_position": session.history_position,
            "selected_index": session.selected_index,
            "is_searching": session.is_searching,
            "search_query": session.search_query,
        }

        logger.info(f"Loaded session '{session.name}' (ID: {session_id})")
        return browser_state

    def get_default_session(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recently used session.

        Returns:
            Browser state from the most recent session, or None if no sessions
        """
        if not self.sessions:
            return None

        # Find most recently used session
        latest_session = max(self.sessions.values(), key=lambda s: s.last_used)
        return self.load_session(latest_session.session_id)

    def list_sessions(self) -> List[BrowserSession]:
        """
        Get list of all sessions, sorted by last used time.

        Returns:
            List of BrowserSession objects
        """
        return sorted(self.sessions.values(), key=lambda s: s.last_used, reverse=True)

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: ID of the session to delete

        Returns:
            True if successful, False otherwise
        """
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found")
            return False

        session_name = self.sessions[session_id].name
        del self.sessions[session_id]

        if self._save_sessions():
            logger.info(f"Deleted session '{session_name}' (ID: {session_id})")
            return True
        else:
            logger.error(f"Failed to delete session {session_id}")
            return False

    def rename_session(self, session_id: str, new_name: str) -> bool:
        """
        Rename a session.

        Args:
            session_id: ID of the session to rename
            new_name: New name for the session

        Returns:
            True if successful, False otherwise
        """
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found")
            return False

        old_name = self.sessions[session_id].name
        self.sessions[session_id].name = new_name

        if self._save_sessions():
            logger.info(f"Renamed session '{old_name}' to '{new_name}'")
            return True
        else:
            logger.error(f"Failed to rename session {session_id}")
            return False

    def _cleanup_old_sessions(self) -> None:
        """
        Remove old sessions if we exceed max_sessions.
        """
        if len(self.sessions) <= self.max_sessions:
            return

        # Sort by last used time and keep only the most recent ones
        sessions_by_time = sorted(self.sessions.values(), key=lambda s: s.last_used, reverse=True)
        sessions_to_remove = sessions_by_time[self.max_sessions:]

        # Remove old sessions
        for session in sessions_to_remove:
            logger.info(
                f"Removing old session '{
                    session.name}' (ID: {
                    session.session_id})"
            )
            del self.sessions[session.session_id]

    def export_sessions(self, export_path: Union[str, Path]) -> bool:
        """
        Export all sessions to a file.

        Args:
            export_path: Path to export file

        Returns:
            True if successful, False otherwise
        """
        export_path = Path(export_path)

        try:
            export_data = {
                "exported_at": datetime.now().isoformat(),
                "sessions": {sid: session.to_dict() for sid, session in self.sessions.items()},
            }

            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, default=str)

            logger.info(f"Exported {len(self.sessions)} sessions to {export_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export sessions: {e}")
            return False

    def import_sessions(self, import_path: Union[str, Path], merge: bool = True) -> bool:
        """
        Import sessions from a file.

        Args:
            import_path: Path to import file
            merge: If True, merge with existing sessions; if False, replace

        Returns:
            True if successful, False otherwise
        """
        import_path = Path(import_path)

        if not import_path.exists():
            logger.error(f"Import file not found: {import_path}")
            return False

        try:
            with open(import_path, "r", encoding="utf-8") as f:
                import_data = json.load(f)

            imported_sessions = import_data.get("sessions", {})

            if not merge:
                self.sessions.clear()

            imported_count = 0
            for session_id, session_data in imported_sessions.items():
                try:
                    session = BrowserSession.from_dict(session_data)
                    self.sessions[session_id] = session
                    imported_count += 1
                except Exception as e:
                    logger.warning(f"Failed to import session {session_id}: {e}")

            if self._save_sessions():
                logger.info(f"Imported {imported_count} sessions from {import_path}")
                return True
            else:
                logger.error("Failed to save imported sessions")
                return False

        except Exception as e:
            logger.error(f"Failed to import sessions: {e}")
            return False

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a session.

        Args:
            session_id: ID of the session

        Returns:
            Dictionary with session information, or None if not found
        """
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]
        return {
            "id": session.session_id,
            "name": session.name,
            "description": session.description,
            "tags": session.tags[:],
            "created_at": session.created_datetime.isoformat(),
            "last_used": session.last_used_datetime.isoformat(),
            "current_url": session.current_url,
            "history_count": len(session.history),
            "is_searching": session.is_searching,
            "search_query": session.search_query if session.is_searching else None,
        }
