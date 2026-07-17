"""Shared test fixtures for Chrome Bridge tests."""

import os
import sys
import pytest

# Ensure the project root is on sys.path
_PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_DIR not in sys.path:
    sys.path.insert(0, _PROJECT_DIR)


@pytest.fixture
def sample_tabs():
    """Sample tab list for testing."""
    return [
        {"id": 1, "title": "Google", "url": "https://www.google.com", "active": True},
        {"id": 2, "title": "GitHub", "url": "https://github.com", "active": False},
        {"id": 3, "title": "Example", "url": "https://www.example.com", "active": False},
    ]
