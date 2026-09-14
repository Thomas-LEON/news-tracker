import sys
from pathlib import Path

repo_root = str(Path(__file__).resolve().parent.parent)
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

import datetime
import re
from unittest.mock import patch
import pytest

import news_tracker


def test_github_actions_skip_when_report_exists(monkeypatch, tmp_path):
    """When env var GITHUB_ACTIONS='true' AND a report file for today already exists,

    the script should exit with sys.exit(0).
    """
    monkeypatch.setenv('GITHUB_ACTIONS', 'true')
    monkeypatch.setattr(news_tracker, '__file__', str(tmp_path / 'news_tracker.py'))

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    dummy_report = reports_dir / f"Daily_Threat_Intel_{today_str}.md"
    dummy_report.write_text("# Existing Report for Today", encoding="utf-8")

    with patch.object(news_tracker, 'fetch_recent_news') as mock_fetch, \
         patch.object(news_tracker, 'generate_executive_summary') as mock_gen, \
         patch.object(news_tracker, 'verify_and_correct_report') as mock_verify, \
         patch.object(news_tracker, 'update_databases') as mock_db, \
         patch.object(news_tracker, 'convert_to_html_report') as mock_html:
        with pytest.raises(SystemExit) as exc_info:
            news_tracker.main()
        assert exc_info.value.code == 0
        mock_fetch.assert_not_called()
        mock_gen.assert_not_called()
        mock_verify.assert_not_called()
        mock_db.assert_not_called()
        mock_html.assert_not_called()


def test_no_skip_when_not_github_actions(monkeypatch, tmp_path):
    """When GITHUB_ACTIONS is not set, even if report exists, the script should NOT skip

    (it should continue). Mock fetch_recent_news to return empty list so it exits early
    for a different reason.
    """
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    monkeypatch.setattr(news_tracker, '__file__', str(tmp_path / 'news_tracker.py'))

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    dummy_report = reports_dir / f"Daily_Threat_Intel_{today_str}.md"
    dummy_report.write_text("# Existing Report for Today", encoding="utf-8")

    with patch.object(news_tracker, 'fetch_recent_news', return_value=[]) as mock_fetch, \
         patch.object(news_tracker, 'generate_executive_summary') as mock_gen, \
         patch.object(news_tracker, 'verify_and_correct_report') as mock_verify, \
         patch.object(news_tracker, 'update_databases') as mock_db, \
         patch.object(news_tracker, 'convert_to_html_report') as mock_html:
        # Script should not raise SystemExit, it continues to fetch_recent_news
        news_tracker.main()
        mock_fetch.assert_called_once()
        mock_gen.assert_not_called()
        mock_verify.assert_not_called()
        mock_db.assert_not_called()
        mock_html.assert_not_called()


def test_skipped_when_no_articles(monkeypatch, tmp_path):
    """When fetch_recent_news returns empty list, the function should return early

    without creating any report.
    """
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    monkeypatch.setattr(news_tracker, '__file__', str(tmp_path / 'news_tracker.py'))

    with patch('news_tracker.fetch_recent_news', return_value=[]) as mock_fetch, \
         patch('news_tracker.generate_executive_summary') as mock_gen, \
         patch('news_tracker.verify_and_correct_report') as mock_verify, \
         patch('news_tracker.update_databases') as mock_db, \
         patch('news_tracker.convert_to_html_report') as mock_html:
        news_tracker.main()
        mock_fetch.assert_called_once()
        mock_gen.assert_not_called()
        mock_verify.assert_not_called()
        mock_db.assert_not_called()
        mock_html.assert_not_called()

    reports_dir = tmp_path / "reports"
    assert not reports_dir.exists() or len(list(reports_dir.iterdir())) == 0


def test_skipped_when_llm_returns_skipped(monkeypatch, tmp_path):
    """When generate_executive_summary returns 'SKIPPED', the function should return early."""
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    monkeypatch.setattr(news_tracker, '__file__', str(tmp_path / 'news_tracker.py'))

    sample_articles = [
        {
            "title": "Minor incident not meeting criteria",
            "link": "https://example.com/article1",
            "summary": "Low-impact non-banking event.",
            "source": "Cyber Feed",
            "published": "2026-09-14 09:00:00 UTC"
        }
    ]

    with patch('news_tracker.fetch_recent_news', return_value=sample_articles) as mock_fetch, \
         patch('news_tracker.generate_executive_summary', return_value='SKIPPED') as mock_gen, \
         patch('news_tracker.verify_and_correct_report') as mock_verify, \
         patch('news_tracker.update_databases') as mock_db, \
         patch('news_tracker.convert_to_html_report') as mock_html:
        news_tracker.main()
        mock_fetch.assert_called_once()
        mock_gen.assert_called_once()
        mock_verify.assert_not_called()
        mock_db.assert_not_called()
        mock_html.assert_not_called()

    reports_dir = tmp_path / "reports"
    assert not reports_dir.exists() or len(list(reports_dir.iterdir())) == 0


def test_plaintext_stripping():
    """Verify that the plaintext conversion strips markdown:

    **bold** becomes bold, ## Heading becomes Heading, --- becomes separator line.
    Tested inline without importing, testing regex logic directly.
    """
    # Test bold and italic stripping
    txt = '**bold text** and *italic*'
    txt = re.sub(r'\*\*([^*]+)\*\*', r'\1', txt)
    txt = re.sub(r'\*([^*]+)\*', r'\1', txt)
    assert txt == 'bold text and italic'

    # Test headings stripping
    heading_txt = '## Heading\n### Subheading\n# Title'
    heading_txt = re.sub(r'^#{1,6}\s+', '', heading_txt, flags=re.MULTILINE)
    assert heading_txt == 'Heading\nSubheading\nTitle'

    # Test separator line replacement
    sep_txt = 'Section 1\n---\nSection 2'
    sep_txt = sep_txt.replace('---', '─' * 60)
    assert sep_txt == f'Section 1\n{"─" * 60}\nSection 2'

    # Test complete combined stripping logic as used in news_tracker.py
    raw_content = (
        "# Daily Threat Intel Report\n"
        "**Date:** September 14, 2026\n\n"
        "## Critical Cyber Threat\n"
        "This is **critical** and *urgent*.\n"
        "---\n"
        "## Secondary Threat\n"
        "Additional details here."
    )
    stripped = re.sub(r'\*\*([^*]+)\*\*', r'\1', raw_content)
    stripped = re.sub(r'\*([^*]+)\*', r'\1', stripped)
    stripped = re.sub(r'^#{1,6}\s+', '', stripped, flags=re.MULTILINE)
    stripped = stripped.replace('---', '─' * 60)

    assert '**' not in stripped
    assert 'critical and urgent' in stripped
    assert '##' not in stripped
    assert 'Critical Cyber Threat' in stripped
    assert '─' * 60 in stripped


def test_toc_generation():
    """Given a final_report containing ## Title One and ## Title Two,

    verify the TOC generation logic produces 1. Title One\n2. Title Two\n.
    Tested inline testing regex and formatting logic directly.
    """
    final_report = 'Some text\n## Title One\nBody\n---\n## Title Two\nBody'
    titles = re.findall(r'^## (.*)', final_report, re.MULTILINE)
    assert titles == ['Title One', 'Title Two']
    toc = ''
    for idx, title in enumerate(titles, 1):
        toc += f'{idx}. {title.strip()}\n'
    assert '1. Title One' in toc
    assert '2. Title Two' in toc
    assert toc == '1. Title One\n2. Title Two\n'


def test_main_full_flow_success(monkeypatch, tmp_path):
    """Test full successful execution flow of main() when articles exist and AI generates report."""
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    monkeypatch.setattr(news_tracker, '__file__', str(tmp_path / 'news_tracker.py'))
    monkeypatch.setattr(news_tracker, 'OUTPUT_FORMAT', 'html')

    sample_articles = [
        {
            "title": "Ransomware targets financial institution",
            "link": "https://example.com/news1",
            "summary": "Ransomware incident details",
            "source": "Security Feed",
            "published": "2026-09-14 00:00:00 UTC"
        }
    ]
    draft_summary = (
        "*(Auditable Metrics - Threat Capability: 8/10 | Event Frequency: 7/10 | Business Impact: 9/10)*\n\n"
        "## Ransomware Group Hits Major Bank\n"
        "A sophisticated attack was detected targeting core banking infrastructure."
    )
    verified_summary = (
        "## Ransomware Group Hits Major Bank\n"
        "A sophisticated attack was detected targeting core banking infrastructure."
    )
    dummy_html = "<html><body><h1>Threat Intel Newsletter</h1></body></html>"

    with patch('news_tracker.fetch_recent_news', return_value=sample_articles) as mock_fetch, \
         patch('news_tracker.generate_executive_summary', return_value=draft_summary) as mock_gen, \
         patch('news_tracker.verify_and_correct_report', return_value=verified_summary) as mock_verify, \
         patch('news_tracker.update_databases') as mock_db, \
         patch('news_tracker.convert_to_html_report', return_value=dummy_html) as mock_html:

        news_tracker.main()

        mock_fetch.assert_called_once()
        mock_gen.assert_called_once()
        mock_verify.assert_called_once()
        mock_db.assert_called_once()
        mock_html.assert_called_once()

    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    md_file = tmp_path / "reports" / f"Daily_Threat_Intel_{today_str}.md"
    txt_file = tmp_path / "plaintext" / f"Daily_Threat_Intel_{today_str}.txt"
    eml_file = tmp_path / "newsletters" / f"Daily_Threat_Intel_{today_str}.eml"

    assert md_file.exists()
    assert txt_file.exists()
    assert eml_file.exists()

    md_content = md_file.read_text(encoding="utf-8")
    assert "Threat Score" in md_content
    assert "Executive Summary - Incidents:" in md_content
    assert "1. Ransomware Group Hits Major Bank" in md_content

    txt_content = txt_file.read_text(encoding="utf-8")
    assert "Ransomware Group Hits Major Bank" in txt_content
    assert "**" not in txt_content


def test_skipped_when_auditor_returns_skipped(monkeypatch, tmp_path):
    """When verify_and_correct_report returns 'SKIPPED', the function should return early

    without saving files or updating the database.
    """
    monkeypatch.delenv('GITHUB_ACTIONS', raising=False)
    monkeypatch.setattr(news_tracker, '__file__', str(tmp_path / 'news_tracker.py'))

    sample_articles = [
        {
            "title": "Article 1",
            "link": "https://example.com/1",
            "summary": "Summary",
            "source": "Feed",
            "published": "2026-09-14 00:00:00 UTC"
        }
    ]
    draft_summary = (
        "*(Auditable Metrics - Threat Capability: 5/10 | Event Frequency: 5/10 | Business Impact: 5/10)*\n\n"
        "## Hallucinated Title\nDraft content"
    )

    with patch('news_tracker.fetch_recent_news', return_value=sample_articles) as mock_fetch, \
         patch('news_tracker.generate_executive_summary', return_value=draft_summary) as mock_gen, \
         patch('news_tracker.verify_and_correct_report', return_value='SKIPPED') as mock_verify, \
         patch('news_tracker.update_databases') as mock_db, \
         patch('news_tracker.convert_to_html_report') as mock_html:

        news_tracker.main()

        mock_fetch.assert_called_once()
        mock_gen.assert_called_once()
        mock_verify.assert_called_once()
        mock_db.assert_not_called()
        mock_html.assert_not_called()

    reports_dir = tmp_path / "reports"
    assert not reports_dir.exists() or len(list(reports_dir.iterdir())) == 0
