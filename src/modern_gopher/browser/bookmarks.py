"""
Bookmark management for the Modern Gopher browser.

This module provides functionality to save, organize, and manage
Gopher bookmarks for easy navigation.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional

logger = logging.getLogger(__name__)


class Bookmark(NamedTuple):
    """Represents a single bookmark entry."""
    url: str
    title: str
    description: str = ""
    tags: List[str] = []
    created_at: str = ""
    last_visited: str = ""
    visit_count: int = 0

    def to_dict(self) -> Dict:
        """Convert bookmark to dictionary for JSON serialization."""
        return {
            'url': self.url,
            'title': self.title,
            'description': self.description,
            'tags': list(self.tags),
            'created_at': self.created_at,
            'last_visited': self.last_visited,
            'visit_count': self.visit_count
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Bookmark':
        """Create bookmark from dictionary."""
        return cls(
            url=data.get('url', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            tags=data.get('tags', []),
            created_at=data.get('created_at', ''),
            last_visited=data.get('last_visited', ''),
            visit_count=data.get('visit_count', 0)
        )


class BookmarkManager:
    """Manages Gopher bookmarks with persistence and organization."""

    def __init__(self, bookmarks_file: Optional[str] = None):
        """
        Initialize the bookmark manager.

        Args:
            bookmarks_file: Path to bookmarks JSON file. If None, uses default location.
        """
        if bookmarks_file is None:
            # Use standard config directory
            config_dir = Path.home() / '.config' / 'modern-gopher'
            config_dir.mkdir(parents=True, exist_ok=True)
            self.bookmarks_file = config_dir / 'bookmarks.json'
        else:
            self.bookmarks_file = Path(bookmarks_file)

        self._bookmarks: Dict[str, Bookmark] = {}
        self._load_bookmarks()

    def _load_bookmarks(self) -> None:
        """Load bookmarks from file."""
        try:
            if self.bookmarks_file.exists():
                with open(self.bookmarks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._bookmarks = {
                        url: Bookmark.from_dict(bookmark_data)
                        for url, bookmark_data in data.items()
                    }
                logger.debug(
                    f"Loaded {len(self._bookmarks)} bookmarks from {self.bookmarks_file}")
            else:
                # Create with some default bookmarks
                self._create_default_bookmarks()
        except Exception as e:
            logger.error(f"Error loading bookmarks: {e}")
            self._bookmarks = {}

    def _save_bookmarks(self) -> None:
        """Save bookmarks to file."""
        try:
            # Ensure directory exists
            self.bookmarks_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.bookmarks_file, 'w', encoding='utf-8') as f:
                data = {
                    url: bookmark.to_dict()
                    for url, bookmark in self._bookmarks.items()
                }
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(
                f"Saved {len(self._bookmarks)} bookmarks to {self.bookmarks_file}")
        except Exception as e:
            logger.error(f"Error saving bookmarks: {e}")

    def _create_default_bookmarks(self) -> None:
        """Create some default bookmarks for new users."""
        default_bookmarks = [
            Bookmark(
                url="gopher://gopher.floodgap.com",
                title="Floodgap Gopher Server",
                description="One of the most popular and well-maintained Gopher servers",
                tags=["popular", "reference"],
                created_at=datetime.now().isoformat()
            ),
            Bookmark(
                url="gopher://sdf.org",
                title="SDF Public Access UNIX System",
                description="Historic public access UNIX system with Gopher presence",
                tags=["historic", "unix"],
                created_at=datetime.now().isoformat()
            ),
            Bookmark(
                url="gopher://circumlunar.space",
                title="Circumlunar Space",
                description="Modern Gopher community hub",
                tags=["community", "modern"],
                created_at=datetime.now().isoformat()
            ),
            Bookmark(
                url="gopher://gopher.floodgap.com/7/v2/vs",
                title="Veronica-2 Search",
                description="Search engine for Gopherspace",
                tags=["search", "tool"],
                created_at=datetime.now().isoformat()
            )
        ]

        for bookmark in default_bookmarks:
            self._bookmarks[bookmark.url] = bookmark

        self._save_bookmarks()

    def add(
            self,
            url: str,
            title: str = "",
            description: str = "",
            tags: List[str] = None) -> bool:
        """Add a new bookmark.

        Args:
            url: The Gopher URL to bookmark
            title: Display title for the bookmark
            description: Optional description
            tags: Optional list of tags for organization

        Returns:
            True if bookmark was added, False if it already exists
        """
        if url in self._bookmarks:
            return False

        if not title:
            title = url

        bookmark = Bookmark(
            url=url,
            title=title,
            description=description,
            tags=tags or [],
            created_at=datetime.now().isoformat(),
            visit_count=0
        )

        self._bookmarks[url] = bookmark
        self._save_bookmarks()
        logger.info(f"Added bookmark: {title} ({url})")
        return True

    def remove(self, url: str) -> bool:
        """Remove a bookmark.

        Args:
            url: The URL to remove

        Returns:
            True if bookmark was removed, False if it didn't exist
        """
        if url in self._bookmarks:
            bookmark = self._bookmarks.pop(url)
            self._save_bookmarks()
            logger.info(f"Removed bookmark: {bookmark.title} ({url})")
            return True
        return False

    def update(self, url: str, **kwargs) -> bool:
        """Update an existing bookmark.

        Args:
            url: The URL of the bookmark to update
            **kwargs: Fields to update (title, description, tags)

        Returns:
            True if bookmark was updated, False if it doesn't exist
        """
        if url not in self._bookmarks:
            return False

        old_bookmark = self._bookmarks[url]
        updated_data = old_bookmark.to_dict()

        # Update allowed fields
        for field in ['title', 'description', 'tags']:
            if field in kwargs:
                updated_data[field] = kwargs[field]

        self._bookmarks[url] = Bookmark.from_dict(updated_data)
        self._save_bookmarks()
        logger.info(f"Updated bookmark: {url}")
        return True

    def is_bookmarked(self, url: str) -> bool:
        """Check if a URL is bookmarked.

        Args:
            url: The URL to check

        Returns:
            True if the URL is bookmarked
        """
        return url in self._bookmarks

    def get(self, url: str) -> Optional[Bookmark]:
        """Get a specific bookmark.

        Args:
            url: The URL to look up

        Returns:
            The bookmark if found, None otherwise
        """
        return self._bookmarks.get(url)

    def get_all(self) -> List[Bookmark]:
        """Get all bookmarks.

        Returns:
            List of all bookmarks, sorted by title
        """
        return sorted(self._bookmarks.values(), key=lambda b: b.title.lower())

    def search(self, query: str) -> List[Bookmark]:
        """Search bookmarks by title, description, or tags.

        Args:
            query: Search query string

        Returns:
            List of matching bookmarks
        """
        query_lower = query.lower()
        matches = []

        for bookmark in self._bookmarks.values():
            # Check title
            if query_lower in bookmark.title.lower():
                matches.append(bookmark)
                continue

            # Check description
            if query_lower in bookmark.description.lower():
                matches.append(bookmark)
                continue

            # Check tags
            if any(query_lower in tag.lower() for tag in bookmark.tags):
                matches.append(bookmark)
                continue

            # Check URL
            if query_lower in bookmark.url.lower():
                matches.append(bookmark)

        return sorted(matches, key=lambda b: b.title.lower())

    def get_by_tag(self, tag: str) -> List[Bookmark]:
        """Get bookmarks by tag.

        Args:
            tag: The tag to filter by

        Returns:
            List of bookmarks with the specified tag
        """
        tag_lower = tag.lower()
        return [
            bookmark for bookmark in self._bookmarks.values()
            if any(t.lower() == tag_lower for t in bookmark.tags)
        ]

    def get_all_tags(self) -> List[str]:
        """Get all unique tags used in bookmarks.

        Returns:
            Sorted list of all tags
        """
        all_tags = set()
        for bookmark in self._bookmarks.values():
            all_tags.update(bookmark.tags)
        return sorted(all_tags)

    def record_visit(self, url: str) -> None:
        """Record a visit to a bookmarked URL.

        Args:
            url: The URL that was visited
        """
        if url in self._bookmarks:
            old_bookmark = self._bookmarks[url]
            updated_data = old_bookmark.to_dict()
            updated_data['last_visited'] = datetime.now().isoformat()
            updated_data['visit_count'] = old_bookmark.visit_count + 1

            self._bookmarks[url] = Bookmark.from_dict(updated_data)
            self._save_bookmarks()

    def get_most_visited(self, limit: int = 10) -> List[Bookmark]:
        """Get the most frequently visited bookmarks.

        Args:
            limit: Maximum number of bookmarks to return

        Returns:
            List of most visited bookmarks
        """
        return sorted(
            self._bookmarks.values(),
            key=lambda b: b.visit_count,
            reverse=True
        )[:limit]

    def get_recent(self, limit: int = 10) -> List[Bookmark]:
        """Get recently visited bookmarks.

        Args:
            limit: Maximum number of bookmarks to return

        Returns:
            List of recently visited bookmarks
        """
        # Filter bookmarks that have been visited
        visited = [b for b in self._bookmarks.values() if b.last_visited]

        return sorted(
            visited,
            key=lambda b: b.last_visited,
            reverse=True
        )[:limit]

    def import_bookmarks(self, file_path: str) -> int:
        """Import bookmarks from a JSON file.

        Args:
            file_path: Path to the JSON file containing bookmarks

        Returns:
            Number of bookmarks imported
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            imported_count = 0
            for url, bookmark_data in data.items():
                if url not in self._bookmarks:
                    self._bookmarks[url] = Bookmark.from_dict(bookmark_data)
                    imported_count += 1

            if imported_count > 0:
                self._save_bookmarks()

            logger.info(
                f"Imported {imported_count} new bookmarks from {file_path}")
            return imported_count

        except Exception as e:
            logger.error(f"Error importing bookmarks: {e}")
            return 0

    def export_bookmarks(self, file_path: str) -> bool:
        """Export bookmarks to a JSON file.

        Args:
            file_path: Path where to save the bookmarks

        Returns:
            True if export was successful
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                data = {
                    url: bookmark.to_dict()
                    for url, bookmark in self._bookmarks.items()
                }
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(
                f"Exported {len(self._bookmarks)} bookmarks to {file_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting bookmarks: {e}")
            return False

    def clear_all(self) -> int:
        """Remove all bookmarks.

        Returns:
            Number of bookmarks that were removed
        """
        count = len(self._bookmarks)
        self._bookmarks.clear()
        self._save_bookmarks()
        logger.info(f"Cleared all {count} bookmarks")
        return count
