"""Tests for RSS feed fetching and filtering."""

import sys
import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Ensure news-tracker root is on sys.path
sys.path.insert(0, 'C:/Users/Karine/.gemini/antigravity/scratch/news-tracker')
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import news_tracker
from news_tracker import fetch_recent_news


@pytest.fixture
def mock_recent_feed():
    """Create a mock feed object containing one article published 1 hour ago."""
    mock_entry = MagicMock()
    mock_entry.title = 'Test Article'
    mock_entry.link = 'https://example.com/test'
    mock_entry.get.return_value = 'Test summary'
    mock_entry.published_parsed = (
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)
    ).timetuple()

    mock_feed = MagicMock()
    mock_feed.entries = [mock_entry]
    mock_feed.feed.get.return_value = 'Test Source'
    return mock_feed


@pytest.fixture
def mock_old_feed():
    """Create a mock feed object containing one article published 3 days ago."""
    mock_entry = MagicMock()
    mock_entry.title = 'Old Article'
    mock_entry.link = 'https://example.com/old'
    mock_entry.get.return_value = 'Old summary'
    mock_entry.published_parsed = (
        datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=3)
    ).timetuple()

    mock_feed = MagicMock()
    mock_feed.entries = [mock_entry]
    mock_feed.feed.get.return_value = 'Test Source'
    return mock_feed


@patch("news_tracker.RSS_FEEDS", [])
def test_returns_empty_on_no_feeds():
    """Verify that fetch_recent_news returns an empty list when RSS_FEEDS is empty."""
    articles = fetch_recent_news()
    assert articles == []
    assert len(articles) == 0


@patch("news_tracker.RSS_FEEDS", ["https://example.com/feed"])
@patch("news_tracker.feedparser.parse")
def test_parses_recent_article(mock_parse, mock_recent_feed):
    """Verify that an article published 1 hour ago is correctly parsed and included."""
    mock_parse.return_value = mock_recent_feed

    articles = fetch_recent_news()
    assert len(articles) == 1
    assert articles[0]["title"] == "Test Article"
    assert articles[0]["link"] == "https://example.com/test"
    assert articles[0]["summary"] == "Test summary"
    assert articles[0]["source"] == "Test Source"


@patch("news_tracker.RSS_FEEDS", ["https://example.com/feed"])
@patch("news_tracker.feedparser.parse")
def test_filters_old_article(mock_parse, mock_old_feed):
    """Verify that an article published 3 days ago is filtered out (excluded)."""
    mock_parse.return_value = mock_old_feed

    articles = fetch_recent_news()
    assert articles == []
    assert len(articles) == 0


@patch("news_tracker.RSS_FEEDS", ["https://example.com/feed"])
@patch("news_tracker.feedparser.parse")
def test_handles_feed_error(mock_parse):
    """Verify that if feedparser raises an Exception, function returns empty list without crashing."""
    mock_parse.side_effect = Exception("Connection timed out / DNS lookup failed")

    articles = fetch_recent_news()
    assert isinstance(articles, list)
    assert articles == []


@patch("news_tracker.RSS_FEEDS", ["https://example.com/feed"])
@patch("news_tracker.feedparser.parse")
def test_article_dict_structure(mock_parse, mock_recent_feed):
    """Verify that returned article dict contains all expected keys: title, link, summary, source, published."""
    mock_parse.return_value = mock_recent_feed

    articles = fetch_recent_news()
    assert len(articles) == 1
    article = articles[0]

    expected_keys = {"title", "link", "summary", "source", "published"}
    assert set(article.keys()) == expected_keys
    assert article["title"] == "Test Article"
    assert article["link"] == "https://example.com/test"
    assert article["summary"] == "Test summary"
    assert article["source"] == "Test Source"
    assert isinstance(article["published"], str)
