#!/usr/bin/env python3
"""
Demo script for session management functionality.
"""

import sys
import os
import tempfile
import time
sys.path.insert(0, 'src')

from modern_gopher.browser.sessions import SessionManager
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def demo_session_management():
    """Demonstrate session management functionality."""
    console.print(Panel.fit(
        "🗂️  Session Management Demo",
        title="Modern Gopher",
        subtitle="Testing session save/load functionality"
    ))
    
    # Use temporary file for demo
    temp_dir = tempfile.mkdtemp()
    session_file = os.path.join(temp_dir, 'demo_sessions.json')
    
    try:
        # Create session manager
        manager = SessionManager(
            session_file=session_file,
            backup_sessions=True,
            max_sessions=10
        )
        
        console.print("\n📝 Creating sample browser sessions...")
        
        # Create sample browser states
        sample_sessions = [
            {
                'browser_state': {
                    'current_url': 'gopher://gopher.floodgap.com',
                    'history': ['gopher://gopher.floodgap.com'],
                    'history_position': 0,
                    'selected_index': 0,
                    'is_searching': False,
                    'search_query': ''
                },
                'name': 'Floodgap Gopher',
                'description': 'Main Floodgap directory',
                'tags': ['gopher', 'directory']
            },
            {
                'browser_state': {
                    'current_url': 'gopher://sdf.org',
                    'history': ['gopher://sdf.org', 'gopher://sdf.org/users'],
                    'history_position': 1,
                    'selected_index': 3,
                    'is_searching': True,
                    'search_query': 'programming'
                },
                'name': 'SDF - Programming Search',
                'description': 'Searching for programming resources',
                'tags': ['sdf', 'programming', 'search']
            },
            {
                'browser_state': {
                    'current_url': 'gopher://gopherpedia.com',
                    'history': ['gopher://gopherpedia.com', 'gopher://gopherpedia.com/0/lookup?unix'],
                    'history_position': 1,
                    'selected_index': 0,
                    'is_searching': False,
                    'search_query': ''
                },
                'name': 'Gopherpedia - Unix Info',
                'description': 'Looking up Unix information',
                'tags': ['gopherpedia', 'unix', 'reference']
            }
        ]
        
        # Save sessions
        session_ids = []
        for session_data in sample_sessions:
            # Add small delay to ensure different timestamps
            time.sleep(0.1)
            
            session_id = manager.save_session(
                browser_state=session_data['browser_state'],
                session_name=session_data['name'],
                description=session_data['description'],
                tags=session_data['tags']
            )
            session_ids.append(session_id)
            console.print(f"✅ Saved session: {session_data['name']}")
        
        console.print(f"\n📊 Session Management Demo Results:")
        
        # List all sessions
        sessions = manager.list_sessions()
        
        table = Table(title="Saved Browser Sessions")
        table.add_column("Name", style="blue")
        table.add_column("URL", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("History", style="cyan")
        table.add_column("Tags", style="magenta")
        
        for session in sessions:
            status = "🔍 Searching" if session.is_searching else "📖 Browsing"
            if session.is_searching:
                status += f" '{session.search_query}'"
            
            tags_display = ", ".join(session.tags) if session.tags else "None"
            
            table.add_row(
                session.name,
                session.current_url,
                status,
                f"{len(session.history)} items",
                tags_display
            )
        
        console.print(table)
        
        # Test loading a session
        console.print("\n🔄 Testing session restoration...")
        
        # Load the search session
        search_session_id = session_ids[1]  # SDF programming search
        restored_state = manager.load_session(search_session_id)
        
        if restored_state:
            console.print("✅ Session restoration successful!")
            console.print(f"   Restored URL: {restored_state['current_url']}")
            console.print(f"   History position: {restored_state['history_position']}/{len(restored_state['history'])}")
            console.print(f"   Selected item: {restored_state['selected_index']}")
            
            if restored_state['is_searching']:
                console.print(f"   🔍 Search mode: '{restored_state['search_query']}'")
        
        # Test session info
        console.print("\n📋 Session details:")
        for session_id in session_ids[:2]:  # Show first two
            info = manager.get_session_info(session_id)
            if info:
                console.print(f"\n📝 {info['name']}:")
                console.print(f"   ID: {info['id'][:12]}...")
                console.print(f"   Description: {info['description']}")
                console.print(f"   Created: {info['created_at'][:19]}")
                console.print(f"   Tags: {', '.join(info['tags'])}")
        
        # Test export
        console.print("\n💾 Testing session export...")
        export_path = os.path.join(temp_dir, 'exported_sessions.json')
        if manager.export_sessions(export_path):
            console.print(f"✅ Sessions exported to {os.path.basename(export_path)}")
            
            # Show export file size
            size = os.path.getsize(export_path)
            console.print(f"   Export file size: {size} bytes")
        
        # Session management operations
        console.print("\n⚙️  Testing session management operations...")
        
        # Rename a session
        test_session_id = session_ids[0]
        if manager.rename_session(test_session_id, "Floodgap Gopher (Renamed)"):
            console.print("✅ Session renamed successfully")
        
        # Delete a session
        if manager.delete_session(session_ids[-1]):
            console.print("✅ Session deleted successfully")
        
        # Show final session count
        final_sessions = manager.list_sessions()
        console.print(f"\n📈 Final session count: {len(final_sessions)}")
        
        console.print("\n" + "═" * 50)
        console.print("✨ Session Management Demo Complete!")
        console.print("\n💡 Key Features Demonstrated:")
        console.print("   • Save browser sessions with full state")
        console.print("   • Auto-restore most recent session")
        console.print("   • Session search and filtering")
        console.print("   • Export/import session data")
        console.print("   • Session management (rename, delete)")
        console.print("   • CLI integration for all operations")
        
        console.print("\n🚀 Try the CLI commands:")
        console.print("   modern-gopher session list")
        console.print("   modern-gopher session show <session_id>")
        console.print("   modern-gopher session export ~/my_sessions.json")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up temporary files
        try:
            if os.path.exists(session_file):
                os.remove(session_file)
            export_path = os.path.join(temp_dir, 'exported_sessions.json')
            if os.path.exists(export_path):
                os.remove(export_path)
            os.rmdir(temp_dir)
        except Exception as e:
            console.print(f"Cleanup warning: {e}")

if __name__ == "__main__":
    success = demo_session_management()
    sys.exit(0 if success else 1)

