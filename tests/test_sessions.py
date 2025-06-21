#!/usr/bin/env python3
"""
Tests for session management functionality.

This module contains comprehensive tests for the browser session management system,
including session creation, loading, persistence, and error handling.
"""

import json
import tempfile
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

from modern_gopher.browser.sessions import BrowserSession, SessionManager
from modern_gopher.browser.terminal import GopherBrowser
from modern_gopher.config import ModernGopherConfig


class TestBrowserSession:
    """Test the BrowserSession dataclass."""

    def test_session_creation(self):
        """Test basic session creation."""
        session = BrowserSession(
            session_id="test_session",
            name="Test Session",
            created_at=time.time(),
            last_used=time.time(),
            current_url="gopher://example.com",
            history=["gopher://example.com"],
            history_position=0,
            selected_index=0,
        )

        assert session.session_id == "test_session"
        assert session.name == "Test Session"
        assert session.current_url == "gopher://example.com"
        assert len(session.history) == 1
        assert session.tags == []  # Default empty list

    def test_session_with_tags(self):
        """Test session creation with tags."""
        session = BrowserSession(
            session_id="test_session",
            name="Test Session",
            created_at=time.time(),
            last_used=time.time(),
            current_url="gopher://example.com",
            history=[],
            history_position=-1,
            selected_index=0,
            tags=["work", "research"],
        )

        assert session.tags == ["work", "research"]

    def test_datetime_properties(self):
        """Test datetime property conversions."""
        current_time = time.time()
        session = BrowserSession(
            session_id="test_session",
            name="Test Session",
            created_at=current_time,
            last_used=current_time,
            current_url="gopher://example.com",
            history=[],
            history_position=-1,
            selected_index=0,
        )

        assert isinstance(session.created_datetime, datetime)
        assert isinstance(session.last_used_datetime, datetime)

    def test_to_dict(self):
        """Test conversion to dictionary."""
        session = BrowserSession(
            session_id="test_session",
            name="Test Session",
            created_at=1234567890.0,
            last_used=1234567890.0,
            current_url="gopher://example.com",
            history=["gopher://example.com"],
            history_position=0,
            selected_index=0,
            tags=["test"],
        )

        session_dict = session.to_dict()
        assert session_dict["session_id"] == "test_session"
        assert session_dict["name"] == "Test Session"
        assert session_dict["created_at"] == 1234567890.0
        assert session_dict["tags"] == ["test"]

    def test_from_dict(self):
        """Test creation from dictionary."""
        session_data = {
            "session_id": "test_session",
            "name": "Test Session",
            "created_at": 1234567890.0,
            "last_used": 1234567890.0,
            "current_url": "gopher://example.com",
            "history": ["gopher://example.com"],
            "history_position": 0,
            "selected_index": 0,
            "is_searching": False,
            "search_query": "",
            "description": "Test description",
            "tags": ["test"],
        }

        session = BrowserSession.from_dict(session_data)
        assert session.session_id == "test_session"
        assert session.name == "Test Session"
        assert session.description == "Test description"
        assert session.tags == ["test"]


class TestSessionManager:
    """Test the SessionManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.session_file = Path(self.temp_dir) / "test_sessions.json"
        self.manager = SessionManager(
            session_file=str(self.session_file), backup_sessions=True, max_sessions=5
        )

    def test_manager_initialization(self):
        """Test session manager initialization."""
        assert self.manager.session_file == self.session_file
        assert self.manager.backup_sessions is True
        assert self.manager.max_sessions == 5
        assert len(self.manager.sessions) == 0

    def test_save_session(self):
        """Test saving a session."""
        browser_state = {
            "current_url": "gopher://example.com",
            "history": ["gopher://example.com"],
            "history_position": 0,
            "selected_index": 0,
            "is_searching": False,
            "search_query": "",
        }

        session_id = self.manager.save_session(
            browser_state=browser_state,
            session_name="Test Session",
            description="Test description",
            tags=["test"],
        )

        assert session_id
        assert session_id in self.manager.sessions

        session = self.manager.sessions[session_id]
        assert session.name == "Test Session"
        assert session.description == "Test description"
        assert session.tags == ["test"]
        assert session.current_url == "gopher://example.com"

    def test_load_session(self):
        """Test loading a session."""
        # First save a session
        browser_state = {
            "current_url": "gopher://example.com",
            "history": ["gopher://example.com", "gopher://another.com"],
            "history_position": 1,
            "selected_index": 2,
            "is_searching": True,
            "search_query": "test query",
        }

        session_id = self.manager.save_session(browser_state=browser_state)

        # Load the session
        loaded_state = self.manager.load_session(session_id)

        assert loaded_state is not None
        assert loaded_state["current_url"] == "gopher://example.com"
        assert loaded_state["history"] == ["gopher://example.com", "gopher://another.com"]
        assert loaded_state["history_position"] == 1
        assert loaded_state["selected_index"] == 2
        assert loaded_state["is_searching"] is True
        assert loaded_state["search_query"] == "test query"

    def test_load_nonexistent_session(self):
        """Test loading a session that doesn't exist."""
        result = self.manager.load_session("nonexistent_session")
        assert result is None

    def test_get_default_session(self):
        """Test getting the most recently used session."""
        # Save multiple sessions with different last_used times
        browser_state = {
            "current_url": "gopher://example.com",
            "history": [],
            "history_position": -1,
            "selected_index": 0,
            "is_searching": False,
            "search_query": "",
        }

        session_id1 = self.manager.save_session(browser_state=browser_state, session_id="session_1")
        time.sleep(0.01)  # Ensure different timestamps
        session_id2 = self.manager.save_session(browser_state=browser_state, session_id="session_2")

        # The second session should be the default (most recent)
        default_state = self.manager.get_default_session()
        assert default_state is not None

        # Access the session ID of the loaded state by checking which one was
        # updated most recently
        session1 = self.manager.sessions[session_id1]
        session2 = self.manager.sessions[session_id2]
        assert session2.last_used > session1.last_used

    def test_list_sessions(self):
        """Test listing sessions."""
        # Add multiple sessions
        browser_state = {
            "current_url": "gopher://example.com",
            "history": [],
            "history_position": -1,
            "selected_index": 0,
            "is_searching": False,
            "search_query": "",
        }

        self.manager.save_session(
            browser_state=browser_state, session_name="Session 1", session_id="session_1"
        )
        time.sleep(0.01)
        self.manager.save_session(
            browser_state=browser_state, session_name="Session 2", session_id="session_2"
        )

        sessions = self.manager.list_sessions()
        assert len(sessions) == 2

        # Should be sorted by last_used in descending order
        assert sessions[0].name == "Session 2"  # Most recent first
        assert sessions[1].name == "Session 1"

    def test_delete_session(self):
        """Test deleting a session."""
        browser_state = {
            "current_url": "gopher://example.com",
            "history": [],
            "history_position": -1,
            "selected_index": 0,
            "is_searching": False,
            "search_query": "",
        }

        session_id = self.manager.save_session(browser_state=browser_state)
        assert session_id in self.manager.sessions

        result = self.manager.delete_session(session_id)
        assert result is True
        assert session_id not in self.manager.sessions

        # Test deleting nonexistent session
        result = self.manager.delete_session("nonexistent")
        assert result is False

    def test_rename_session(self):
        """Test renaming a session."""
        browser_state = {
            "current_url": "gopher://example.com",
            "history": [],
            "history_position": -1,
            "selected_index": 0,
            "is_searching": False,
            "search_query": "",
        }

        session_id = self.manager.save_session(browser_state=browser_state, session_name="Old Name")

        result = self.manager.rename_session(session_id, "New Name")
        assert result is True
        assert self.manager.sessions[session_id].name == "New Name"

        # Test renaming nonexistent session
        result = self.manager.rename_session("nonexistent", "Some Name")
        assert result is False

    def test_max_sessions_cleanup(self):
        """Test automatic cleanup when max sessions is exceeded."""
        browser_state = {
            "current_url": "gopher://example.com",
            "history": [],
            "history_position": -1,
            "selected_index": 0,
            "is_searching": False,
            "search_query": "",
        }

        # Add more sessions than the limit
        session_ids = []
        for i in range(7):  # max_sessions is 5
            session_id = self.manager.save_session(
                browser_state=browser_state,
                session_name=f"Session {i}",
                # Explicit session IDs to avoid collisions
                session_id=f"session_{i}",
            )
            session_ids.append(session_id)
            time.sleep(0.01)  # Ensure different timestamps

        # Should only have 5 sessions (the 5 most recent)
        assert len(self.manager.sessions) == 5

        # The oldest sessions should be removed
        assert session_ids[0] not in self.manager.sessions  # Oldest
        assert session_ids[1] not in self.manager.sessions  # Second oldest
        assert session_ids[-1] in self.manager.sessions  # Most recent

    def test_session_persistence(self):
        """Test that sessions are saved to and loaded from file."""
        browser_state = {
            "current_url": "gopher://example.com",
            "history": ["gopher://example.com"],
            "history_position": 0,
            "selected_index": 0,
            "is_searching": False,
            "search_query": "",
        }

        session_id = self.manager.save_session(
            browser_state=browser_state, session_name="Persistent Session"
        )

        # Create a new manager instance to test loading
        new_manager = SessionManager(
            session_file=str(self.session_file), backup_sessions=False, max_sessions=10
        )

        assert session_id in new_manager.sessions
        assert new_manager.sessions[session_id].name == "Persistent Session"

    def test_export_sessions(self):
        """Test exporting sessions to a file."""
        browser_state = {
            "current_url": "gopher://example.com",
            "history": [],
            "history_position": -1,
            "selected_index": 0,
            "is_searching": False,
            "search_query": "",
        }

        self.manager.save_session(browser_state=browser_state, session_name="Export Test")

        export_path = Path(self.temp_dir) / "exported_sessions.json"
        result = self.manager.export_sessions(export_path)
        assert result is True
        assert export_path.exists()

        # Verify export content
        with open(export_path, "r") as f:
            export_data = json.load(f)

        assert "exported_at" in export_data
        assert "sessions" in export_data
        assert len(export_data["sessions"]) == 1

    def test_import_sessions(self):
        """Test importing sessions from a file."""
        # Create export data
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "sessions": {
                "imported_session": {
                    "session_id": "imported_session",
                    "name": "Imported Session",
                    "created_at": time.time(),
                    "last_used": time.time(),
                    "current_url": "gopher://imported.com",
                    "history": ["gopher://imported.com"],
                    "history_position": 0,
                    "selected_index": 0,
                    "is_searching": False,
                    "search_query": "",
                    "description": "",
                    "tags": [],
                }
            },
        }

        import_path = Path(self.temp_dir) / "import_sessions.json"
        with open(import_path, "w") as f:
            json.dump(export_data, f)

        result = self.manager.import_sessions(import_path, merge=True)
        assert result is True
        assert "imported_session" in self.manager.sessions
        assert self.manager.sessions["imported_session"].name == "Imported Session"

    def test_get_session_info(self):
        """Test getting detailed session information."""
        browser_state = {
            "current_url": "gopher://example.com",
            "history": ["gopher://example.com", "gopher://other.com"],
            "history_position": 1,
            "selected_index": 0,
            "is_searching": True,
            "search_query": "test",
        }

        session_id = self.manager.save_session(
            browser_state=browser_state,
            session_name="Info Test",
            description="Test description",
            tags=["test", "info"],
        )

        info = self.manager.get_session_info(session_id)
        assert info is not None
        assert info["id"] == session_id
        assert info["name"] == "Info Test"
        assert info["description"] == "Test description"
        assert info["tags"] == ["test", "info"]
        assert info["current_url"] == "gopher://example.com"
        assert info["history_count"] == 2
        assert info["is_searching"] is True
        assert info["search_query"] == "test"

        # Test nonexistent session
        info = self.manager.get_session_info("nonexistent")
        assert info is None


class TestBrowserSessionIntegration:
    """Test session management integration with the browser."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.session_file = Path(self.temp_dir) / "browser_sessions.json"

        # Mock config
        self.mock_config = Mock(spec=ModernGopherConfig)
        self.mock_config.session_enabled = True
        self.mock_config.session_auto_restore = True
        self.mock_config.session_file = str(self.session_file)
        self.mock_config.session_backup_sessions = True
        self.mock_config.session_max_sessions = 5
        self.mock_config.save_session = True
        self.mock_config.initial_url = "gopher://test.com"
        self.mock_config.cache_enabled = False
        self.mock_config.max_history_items = 100
        self.mock_config.bookmarks_file = str(Path(self.temp_dir) / "bookmarks.json")

    @patch("modern_gopher.browser.terminal.GopherClient")
    def test_browser_session_integration(self, mock_client_class):
        """Test session integration with the browser."""
        # Mock the client
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.get_resource.return_value = []

        with patch("modern_gopher.browser.terminal.KeyBindingManager"):
            browser = GopherBrowser(initial_url="gopher://test.com", config=self.mock_config)

            # Test that session manager is initialized
            assert browser.session_manager is not None
            assert isinstance(browser.session_manager, SessionManager)

    @patch("modern_gopher.browser.terminal.GopherClient")
    def test_get_browser_state(self, mock_client_class):
        """Test getting browser state for session saving."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        with patch("modern_gopher.browser.terminal.KeyBindingManager"):
            browser = GopherBrowser(initial_url="gopher://test.com", config=self.mock_config)

            # Set some browser state
            browser.current_url = "gopher://example.com"
            browser.history.add("gopher://example.com")
            browser.selected_index = 2
            browser.is_searching = True
            browser.search_query = "test query"

            state = browser.get_browser_state()

            assert state["current_url"] == "gopher://example.com"
            assert state["history"] == ["gopher://example.com"]
            assert state["history_position"] == 0
            assert state["selected_index"] == 2
            assert state["is_searching"] is True
            assert state["search_query"] == "test query"

    @patch("modern_gopher.browser.terminal.GopherClient")
    def test_save_current_session(self, mock_client_class):
        """Test manual session saving."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        with patch("modern_gopher.browser.terminal.KeyBindingManager"):
            browser = GopherBrowser(initial_url="gopher://test.com", config=self.mock_config)

            # Set browser state
            browser.current_url = "gopher://example.com"
            browser.history.add("gopher://example.com")

            # Simulate saving a session directly (bypass dialog)
            browser_state = browser.get_browser_state()
            browser.session_manager.save_session(
                browser_state=browser_state, session_name="Test Session"
            )

            # Verify session was saved
            sessions = browser.session_manager.list_sessions()
            assert len(sessions) == 1
            assert sessions[0].name == "Test Session"

    @patch("modern_gopher.browser.terminal.GopherClient")
    def test_auto_restore_session(self, mock_client_class):
        """Test automatic session restoration."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # First, create a session to restore
        session_manager = SessionManager(session_file=str(self.session_file), max_sessions=5)

        browser_state = {
            "current_url": "gopher://restored.com",
            "history": ["gopher://restored.com", "gopher://other.com"],
            "history_position": 1,
            "selected_index": 3,
            "is_searching": False,
            "search_query": "",
        }

        session_manager.save_session(browser_state=browser_state, session_name="Restore Test")

        # Now create browser and test restoration
        with patch("modern_gopher.browser.terminal.KeyBindingManager"):
            browser = GopherBrowser(initial_url="gopher://test.com", config=self.mock_config)

            # Test auto restore
            restored = browser.auto_restore_session()

            assert restored is True
            # URL should be restored (note: may have item type appended)
            assert "gopher://restored.com" in browser.current_url
            # History should contain the restored URLs (order may vary due to
            # navigation)
            assert "gopher://restored.com" in browser.history.history
            assert "gopher://other.com" in browser.history.history
            assert browser.selected_index == 3


class TestSessionErrorHandling:
    """Test error handling in session management."""

    def test_session_manager_invalid_file(self):
        """Test session manager with directory creation failure."""
        temp_dir = tempfile.mkdtemp()
        session_file = Path(temp_dir) / "subdir" / "sessions.json"

        # Mock the directory creation to fail
        with patch("pathlib.Path.mkdir", side_effect=OSError("Permission denied")):
            # Should handle directory creation failure gracefully
            try:
                manager = SessionManager(session_file=str(session_file), max_sessions=5)
                # If it doesn't crash, should have empty sessions
                assert len(manager.sessions) == 0
            except OSError:
                # It's acceptable if it fails with OSError for invalid paths
                pass

    def test_corrupted_session_file(self):
        """Test handling of corrupted session file."""
        temp_dir = tempfile.mkdtemp()
        session_file = Path(temp_dir) / "corrupted_sessions.json"

        # Create corrupted JSON file
        with open(session_file, "w") as f:
            f.write("{ invalid json")

        # Should handle corrupted file gracefully
        manager = SessionManager(session_file=str(session_file), max_sessions=5)

        assert len(manager.sessions) == 0

    def test_session_with_missing_fields(self):
        """Test handling of session data with missing fields."""
        temp_dir = tempfile.mkdtemp()
        session_file = Path(temp_dir) / "incomplete_sessions.json"

        # Create session file with missing required fields
        incomplete_session_data = {
            "incomplete_session": {
                "session_id": "incomplete_session",
                "name": "Incomplete Session",
                # Missing required fields like created_at, last_used, etc.
            }
        }

        with open(session_file, "w") as f:
            json.dump(incomplete_session_data, f)

        # Should handle incomplete session data gracefully
        manager = SessionManager(session_file=str(session_file), max_sessions=5)

        # Should not load the incomplete session
        assert "incomplete_session" not in manager.sessions

    @patch("modern_gopher.browser.terminal.GopherClient")
    def test_browser_session_disabled(self, mock_client_class):
        """Test browser behavior when sessions are disabled."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Config with sessions disabled
        mock_config = Mock(spec=ModernGopherConfig)
        mock_config.session_enabled = False
        mock_config.cache_enabled = False
        mock_config.max_history_items = 100
        mock_config.bookmarks_file = "/tmp/bookmarks.json"

        with patch("modern_gopher.browser.terminal.KeyBindingManager"):
            browser = GopherBrowser(initial_url="gopher://test.com", config=mock_config)

            # Session manager should be None
            assert browser.session_manager is None

            # Session methods should handle None gracefully
            browser.save_current_session()  # Should not crash
            restored = browser.auto_restore_session()  # Should return False
            assert restored is False
