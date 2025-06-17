#!/usr/bin/env python3
"""
Tests for the session management functionality.
"""

import pytest
import tempfile
import os
import json
import time
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, 'src')

from modern_gopher.browser.sessions import SessionManager, BrowserSession
from modern_gopher.config import ModernGopherConfig


class TestBrowserSession:
    """Test the BrowserSession dataclass."""
    
    def test_session_creation(self):
        """Test creating a basic session."""
        session = BrowserSession(
            session_id="test_123",
            name="Test Session",
            created_at=1640995200.0,  # 2022-01-01 00:00:00
            last_used=1640995200.0,
            current_url="gopher://example.com",
            history=["gopher://example.com", "gopher://example.com/subdir"],
            history_position=1,
            selected_index=0
        )
        
        assert session.session_id == "test_123"
        assert session.name == "Test Session"
        assert session.current_url == "gopher://example.com"
        assert len(session.history) == 2
        assert session.history_position == 1
        assert session.selected_index == 0
        assert not session.is_searching
        assert session.search_query == ""
        assert session.tags == []
    
    def test_session_with_search_state(self):
        """Test creating a session with search state."""
        session = BrowserSession(
            session_id="search_session",
            name="Search Session",
            created_at=time.time(),
            last_used=time.time(),
            current_url="gopher://example.com",
            history=["gopher://example.com"],
            history_position=0,
            selected_index=2,
            is_searching=True,
            search_query="test query",
            tags=["work", "development"]
        )
        
        assert session.is_searching
        assert session.search_query == "test query"
        assert session.selected_index == 2
        assert "work" in session.tags
        assert "development" in session.tags
    
    def test_session_datetime_properties(self):
        """Test datetime property conversions."""
        timestamp = 1640995200.0  # 2022-01-01 00:00:00
        
        session = BrowserSession(
            session_id="datetime_test",
            name="DateTime Test",
            created_at=timestamp,
            last_used=timestamp + 3600,  # 1 hour later
            current_url="gopher://example.com",
            history=[],
            history_position=-1,
            selected_index=0
        )
        
        assert session.created_datetime.year == 2022
        assert session.created_datetime.month == 1
        assert session.created_datetime.day == 1
        
        assert session.last_used_datetime.hour == 1  # 1 hour after midnight
    
    def test_session_serialization(self):
        """Test session to_dict and from_dict."""
        original = BrowserSession(
            session_id="serialize_test",
            name="Serialization Test",
            created_at=time.time(),
            last_used=time.time(),
            current_url="gopher://test.com",
            history=["gopher://test.com", "gopher://test.com/dir"],
            history_position=1,
            selected_index=3,
            is_searching=True,
            search_query="serialize",
            description="Test description",
            tags=["test", "serialization"]
        )
        
        # Convert to dict and back
        session_dict = original.to_dict()
        restored = BrowserSession.from_dict(session_dict)
        
        # Verify all fields are preserved
        assert restored.session_id == original.session_id
        assert restored.name == original.name
        assert restored.created_at == original.created_at
        assert restored.last_used == original.last_used
        assert restored.current_url == original.current_url
        assert restored.history == original.history
        assert restored.history_position == original.history_position
        assert restored.selected_index == original.selected_index
        assert restored.is_searching == original.is_searching
        assert restored.search_query == original.search_query
        assert restored.description == original.description
        assert restored.tags == original.tags


class TestSessionManager:
    """Test the SessionManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create temporary session file
        self.temp_dir = tempfile.mkdtemp()
        self.session_file = os.path.join(self.temp_dir, 'test_sessions.json')
        
        # Create test browser state
        self.test_browser_state = {
            'current_url': 'gopher://example.com/test',
            'history': ['gopher://example.com', 'gopher://example.com/test'],
            'history_position': 1,
            'selected_index': 2,
            'is_searching': False,
            'search_query': ''
        }
    
    def teardown_method(self):
        """Clean up test fixtures."""
        # Remove temporary files
        if os.path.exists(self.session_file):
            os.remove(self.session_file)
        os.rmdir(self.temp_dir)
    
    def test_session_manager_initialization(self):
        """Test SessionManager initialization."""
        manager = SessionManager(
            session_file=self.session_file,
            backup_sessions=True,
            max_sessions=5
        )
        
        assert manager.session_file == Path(self.session_file)
        assert manager.backup_sessions is True
        assert manager.max_sessions == 5
        assert len(manager.sessions) == 0
    
    def test_save_session_basic(self):
        """Test saving a basic session."""
        manager = SessionManager(session_file=self.session_file)
        
        session_id = manager.save_session(
            browser_state=self.test_browser_state,
            session_name="Test Session"
        )
        
        assert session_id
        assert session_id in manager.sessions
        
        session = manager.sessions[session_id]
        assert session.name == "Test Session"
        assert session.current_url == self.test_browser_state['current_url']
        assert session.history == self.test_browser_state['history']
        assert session.history_position == self.test_browser_state['history_position']
        assert session.selected_index == self.test_browser_state['selected_index']
    
    def test_save_session_auto_name(self):
        """Test saving a session with auto-generated name."""
        manager = SessionManager(session_file=self.session_file)
        
        session_id = manager.save_session(browser_state=self.test_browser_state)
        
        assert session_id
        session = manager.sessions[session_id]
        assert "example.com" in session.name  # Should include hostname
    
    def test_save_session_with_description_and_tags(self):
        """Test saving a session with description and tags."""
        manager = SessionManager(session_file=self.session_file)
        
        session_id = manager.save_session(
            browser_state=self.test_browser_state,
            session_name="Tagged Session",
            description="A test session with tags",
            tags=["test", "development"]
        )
        
        session = manager.sessions[session_id]
        assert session.description == "A test session with tags"
        assert session.tags == ["test", "development"]
    
    def test_load_session(self):
        """Test loading a session."""
        manager = SessionManager(session_file=self.session_file)
        
        # Save a session first
        session_id = manager.save_session(
            browser_state=self.test_browser_state,
            session_name="Load Test"
        )
        
        # Load the session
        loaded_state = manager.load_session(session_id)
        
        assert loaded_state is not None
        assert loaded_state['current_url'] == self.test_browser_state['current_url']
        assert loaded_state['history'] == self.test_browser_state['history']
        assert loaded_state['history_position'] == self.test_browser_state['history_position']
        assert loaded_state['selected_index'] == self.test_browser_state['selected_index']
    
    def test_load_nonexistent_session(self):
        """Test loading a session that doesn't exist."""
        manager = SessionManager(session_file=self.session_file)
        
        loaded_state = manager.load_session("nonexistent_session")
        assert loaded_state is None
    
    def test_get_default_session(self):
        """Test getting the most recently used session."""
        manager = SessionManager(session_file=self.session_file)
        
        # Save multiple sessions with different timestamps
        session1_id = manager.save_session(
            browser_state=self.test_browser_state,
            session_name="Older Session"
        )
        
        time.sleep(0.1)  # Ensure different timestamps
        
        session2_id = manager.save_session(
            browser_state=self.test_browser_state,
            session_name="Newer Session"
        )
        
        # Get default session (should be the newer one)
        default_state = manager.get_default_session()
        
        assert default_state is not None
        # The newer session should be loaded
        assert manager.sessions[session2_id].last_used > manager.sessions[session1_id].last_used
    
    def test_list_sessions(self):
        """Test listing sessions sorted by last used."""
        manager = SessionManager(session_file=self.session_file)
        
        # Save multiple sessions
        session1_id = manager.save_session(
            browser_state=self.test_browser_state,
            session_name="Session 1"
        )
        
        time.sleep(0.1)
        
        session2_id = manager.save_session(
            browser_state=self.test_browser_state,
            session_name="Session 2"
        )
        
        sessions = manager.list_sessions()
        
        assert len(sessions) == 2
        # Should be sorted by last_used in descending order
        assert sessions[0].name == "Session 2"  # Most recent first
        assert sessions[1].name == "Session 1"
    
    def test_delete_session(self):
        """Test deleting a session."""
        manager = SessionManager(session_file=self.session_file)
        
        # Save a session
        session_id = manager.save_session(
            browser_state=self.test_browser_state,
            session_name="To Delete"
        )
        
        assert session_id in manager.sessions
        
        # Delete the session
        result = manager.delete_session(session_id)
        
        assert result is True
        assert session_id not in manager.sessions
    
    def test_delete_nonexistent_session(self):
        """Test deleting a session that doesn't exist."""
        manager = SessionManager(session_file=self.session_file)
        
        result = manager.delete_session("nonexistent")
        assert result is False
    
    def test_rename_session(self):
        """Test renaming a session."""
        manager = SessionManager(session_file=self.session_file)
        
        # Save a session
        session_id = manager.save_session(
            browser_state=self.test_browser_state,
            session_name="Original Name"
        )
        
        # Rename the session
        result = manager.rename_session(session_id, "New Name")
        
        assert result is True
        assert manager.sessions[session_id].name == "New Name"
    
    def test_max_sessions_cleanup(self):
        """Test that old sessions are removed when max_sessions is exceeded."""
        manager = SessionManager(
            session_file=self.session_file,
            max_sessions=2
        )
        
        # Save 3 sessions
        session1_id = manager.save_session(
            browser_state=self.test_browser_state,
            session_name="Session 1"
        )
        
        time.sleep(0.1)
        
        session2_id = manager.save_session(
            browser_state=self.test_browser_state,
            session_name="Session 2"
        )
        
        time.sleep(0.1)
        
        session3_id = manager.save_session(
            browser_state=self.test_browser_state,
            session_name="Session 3"
        )
        
        # Should only have 2 sessions (the 2 most recent)
        assert len(manager.sessions) == 2
        assert session1_id not in manager.sessions  # Oldest should be removed
        assert session2_id in manager.sessions
        assert session3_id in manager.sessions
    
    def test_session_persistence(self):
        """Test that sessions are saved to and loaded from file."""
        # Create manager and save a session
        manager1 = SessionManager(session_file=self.session_file)
        session_id = manager1.save_session(
            browser_state=self.test_browser_state,
            session_name="Persistent Session"
        )
        
        # Create new manager instance (should load from file)
        manager2 = SessionManager(session_file=self.session_file)
        
        assert session_id in manager2.sessions
        assert manager2.sessions[session_id].name == "Persistent Session"
    
    def test_export_sessions(self):
        """Test exporting sessions to a file."""
        manager = SessionManager(session_file=self.session_file)
        
        # Save some sessions
        manager.save_session(
            browser_state=self.test_browser_state,
            session_name="Export Test 1"
        )
        manager.save_session(
            browser_state=self.test_browser_state,
            session_name="Export Test 2"
        )
        
        # Export sessions
        export_path = os.path.join(self.temp_dir, 'exported_sessions.json')
        result = manager.export_sessions(export_path)
        
        assert result is True
        assert os.path.exists(export_path)
        
        # Verify export file content
        with open(export_path, 'r') as f:
            export_data = json.load(f)
        
        assert 'exported_at' in export_data
        assert 'sessions' in export_data
        assert len(export_data['sessions']) == 2
    
    def test_import_sessions(self):
        """Test importing sessions from a file."""
        # Create export data
        export_data = {
            'exported_at': '2022-01-01T00:00:00',
            'sessions': {
                'import_test_1': {
                    'session_id': 'import_test_1',
                    'name': 'Imported Session 1',
                    'created_at': time.time(),
                    'last_used': time.time(),
                    'current_url': 'gopher://imported.com',
                    'history': ['gopher://imported.com'],
                    'history_position': 0,
                    'selected_index': 0,
                    'is_searching': False,
                    'search_query': '',
                    'description': '',
                    'tags': []
                }
            }
        }
        
        # Write export file
        export_path = os.path.join(self.temp_dir, 'import_sessions.json')
        with open(export_path, 'w') as f:
            json.dump(export_data, f)
        
        # Import sessions
        manager = SessionManager(session_file=self.session_file)
        result = manager.import_sessions(export_path)
        
        assert result is True
        assert 'import_test_1' in manager.sessions
        assert manager.sessions['import_test_1'].name == 'Imported Session 1'
    
    def test_get_session_info(self):
        """Test getting detailed session information."""
        manager = SessionManager(session_file=self.session_file)
        
        # Save a session with search state
        search_state = self.test_browser_state.copy()
        search_state['is_searching'] = True
        search_state['search_query'] = 'test search'
        
        session_id = manager.save_session(
            browser_state=search_state,
            session_name="Info Test Session",
            description="Test description",
            tags=["test", "info"]
        )
        
        # Get session info
        info = manager.get_session_info(session_id)
        
        assert info is not None
        assert info['id'] == session_id
        assert info['name'] == "Info Test Session"
        assert info['description'] == "Test description"
        assert info['tags'] == ["test", "info"]
        assert info['current_url'] == search_state['current_url']
        assert info['history_count'] == len(search_state['history'])
        assert info['is_searching'] is True
        assert info['search_query'] == 'test search'
        assert 'created_at' in info
        assert 'last_used' in info


if __name__ == "__main__":
    pytest.main([__file__])

