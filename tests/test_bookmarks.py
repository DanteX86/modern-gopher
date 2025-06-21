"""
Tests for the bookmark management system.
"""

import tempfile
from pathlib import Path

from modern_gopher.browser.bookmarks import Bookmark, BookmarkManager


class TestBookmark:
    """Test the Bookmark class."""

    def test_bookmark_creation(self):
        """Test creating a bookmark."""
        bookmark = Bookmark(
            url="gopher://gopher.floodgap.com",
            title="Floodgap",
            description="Popular Gopher server",
            tags=["popular", "reference"],
        )

        assert bookmark.url == "gopher://gopher.floodgap.com"
        assert bookmark.title == "Floodgap"
        assert bookmark.description == "Popular Gopher server"
        assert bookmark.tags == ["popular", "reference"]

    def test_bookmark_to_dict(self):
        """Test converting bookmark to dictionary."""
        bookmark = Bookmark(url="gopher://test.com", title="Test", visit_count=5)

        data = bookmark.to_dict()
        assert data["url"] == "gopher://test.com"
        assert data["title"] == "Test"
        assert data["visit_count"] == 5

    def test_bookmark_from_dict(self):
        """Test creating bookmark from dictionary."""
        data = {
            "url": "gopher://test.com",
            "title": "Test",
            "description": "Test bookmark",
            "tags": ["test"],
            "visit_count": 3,
        }

        bookmark = Bookmark.from_dict(data)
        assert bookmark.url == "gopher://test.com"
        assert bookmark.title == "Test"
        assert bookmark.description == "Test bookmark"
        assert bookmark.tags == ["test"]
        assert bookmark.visit_count == 3


class TestBookmarkManager:
    """Test the BookmarkManager class."""

    def test_manager_initialization(self):
        """Test bookmark manager initialization."""
        with tempfile.TemporaryDirectory() as temp_dir:
            bookmarks_file = Path(temp_dir) / "bookmarks.json"
            manager = BookmarkManager(str(bookmarks_file))

            # Should have default bookmarks
            bookmarks = manager.get_all()
            assert len(bookmarks) > 0

            # Should have Floodgap as default
            floodgap_urls = [b for b in bookmarks if "floodgap" in b.url]
            assert len(floodgap_urls) > 0

    def test_add_bookmark(self):
        """Test adding a bookmark."""
        with tempfile.TemporaryDirectory() as temp_dir:
            bookmarks_file = Path(temp_dir) / "bookmarks.json"
            manager = BookmarkManager(str(bookmarks_file))

            # Add a bookmark
            result = manager.add(
                "gopher://test.example.com", "Test Site", "A test Gopher site", ["test"]
            )

            assert result is True
            assert manager.is_bookmarked("gopher://test.example.com")

            # Try to add the same bookmark again
            result = manager.add("gopher://test.example.com", "Test Site")
            assert result is False

    def test_remove_bookmark(self):
        """Test removing a bookmark."""
        with tempfile.TemporaryDirectory() as temp_dir:
            bookmarks_file = Path(temp_dir) / "bookmarks.json"
            manager = BookmarkManager(str(bookmarks_file))

            # Add a bookmark
            manager.add("gopher://test.example.com", "Test Site")
            assert manager.is_bookmarked("gopher://test.example.com")

            # Remove it
            result = manager.remove("gopher://test.example.com")
            assert result is True
            assert not manager.is_bookmarked("gopher://test.example.com")

            # Try to remove non-existent bookmark
            result = manager.remove("gopher://nonexistent.com")
            assert result is False

    def test_search_bookmarks(self):
        """Test searching bookmarks."""
        with tempfile.TemporaryDirectory() as temp_dir:
            bookmarks_file = Path(temp_dir) / "bookmarks.json"
            manager = BookmarkManager(str(bookmarks_file))

            # Add test bookmarks
            manager.add(
                "gopher://python.org",
                "Python Documentation",
                "Official Python docs",
                ["python", "docs"],
            )
            manager.add(
                "gopher://golang.org", "Go Documentation", "Official Go docs", ["go", "docs"]
            )

            # Search by title
            results = manager.search("python")
            assert len(results) == 1
            assert results[0].url == "gopher://python.org"

            # Search by tag
            results = manager.search("docs")
            assert len(results) == 2

            # Search by URL
            results = manager.search("golang")
            assert len(results) == 1
            assert results[0].url == "gopher://golang.org"

    def test_get_by_tag(self):
        """Test getting bookmarks by tag."""
        with tempfile.TemporaryDirectory() as temp_dir:
            bookmarks_file = Path(temp_dir) / "bookmarks.json"
            manager = BookmarkManager(str(bookmarks_file))

            # Add test bookmarks
            manager.add("gopher://python.org", "Python", tags=["programming", "python"])
            manager.add("gopher://golang.org", "Go", tags=["programming", "go"])
            manager.add("gopher://news.example.com", "News", tags=["news"])

            # Get programming bookmarks
            programming = manager.get_by_tag("programming")
            assert len(programming) == 2

            # Get news bookmarks
            news = manager.get_by_tag("news")
            assert len(news) == 1
            assert news[0].url == "gopher://news.example.com"

    def test_record_visit(self):
        """Test recording visits to bookmarks."""
        with tempfile.TemporaryDirectory() as temp_dir:
            bookmarks_file = Path(temp_dir) / "bookmarks.json"
            manager = BookmarkManager(str(bookmarks_file))

            # Add a bookmark
            manager.add("gopher://test.com", "Test")
            bookmark = manager.get("gopher://test.com")
            assert bookmark.visit_count == 0

            # Record a visit
            manager.record_visit("gopher://test.com")
            bookmark = manager.get("gopher://test.com")
            assert bookmark.visit_count == 1
            assert bookmark.last_visited != ""

            # Record another visit
            manager.record_visit("gopher://test.com")
            bookmark = manager.get("gopher://test.com")
            assert bookmark.visit_count == 2

    def test_most_visited(self):
        """Test getting most visited bookmarks."""
        with tempfile.TemporaryDirectory() as temp_dir:
            bookmarks_file = Path(temp_dir) / "bookmarks.json"
            manager = BookmarkManager(str(bookmarks_file))

            # Add bookmarks with different visit counts
            manager.add("gopher://site1.com", "Site 1")
            manager.add("gopher://site2.com", "Site 2")
            manager.add("gopher://site3.com", "Site 3")

            # Record visits
            for _ in range(5):
                manager.record_visit("gopher://site2.com")
            for _ in range(2):
                manager.record_visit("gopher://site1.com")
            # site3 has no visits

            # Get most visited
            most_visited = manager.get_most_visited()
            assert len(most_visited) >= 2
            assert most_visited[0].url == "gopher://site2.com"  # 5 visits
            assert most_visited[1].url == "gopher://site1.com"  # 2 visits

    def test_persistence(self):
        """Test that bookmarks persist across manager instances."""
        with tempfile.TemporaryDirectory() as temp_dir:
            bookmarks_file = Path(temp_dir) / "bookmarks.json"

            # Create first manager and add bookmark
            manager1 = BookmarkManager(str(bookmarks_file))
            manager1.add("gopher://persistent.com", "Persistent Test")

            # Create second manager and check bookmark exists
            manager2 = BookmarkManager(str(bookmarks_file))
            assert manager2.is_bookmarked("gopher://persistent.com")
            bookmark = manager2.get("gopher://persistent.com")
            assert bookmark.title == "Persistent Test"

    def test_export_import(self):
        """Test exporting and importing bookmarks."""
        with tempfile.TemporaryDirectory() as temp_dir:
            bookmarks_file = Path(temp_dir) / "bookmarks.json"
            export_file = Path(temp_dir) / "export.json"

            # Create manager and add bookmarks
            manager1 = BookmarkManager(str(bookmarks_file))
            manager1.add("gopher://export1.com", "Export Test 1")
            manager1.add("gopher://export2.com", "Export Test 2")

            # Export bookmarks
            result = manager1.export_bookmarks(str(export_file))
            assert result is True
            assert export_file.exists()

            # Create new manager and import
            manager2 = BookmarkManager(str(Path(temp_dir) / "new_bookmarks.json"))
            imported_count = manager2.import_bookmarks(str(export_file))

            # Should import the 2 test bookmarks plus any defaults that weren't
            # already there
            assert imported_count >= 2
            assert manager2.is_bookmarked("gopher://export1.com")
            assert manager2.is_bookmarked("gopher://export2.com")
