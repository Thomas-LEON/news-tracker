import sys
from pathlib import Path
import pytest

sys.path.insert(0, 'C:/Users/Karine/.gemini/antigravity/scratch/news-tracker')
from news_tracker import _md_section_to_html, convert_to_html_report

SAMPLE_REPORT = '''🟠 **Threat Score:** 60/100

## Test Incident Title (September 14, 2026)

**Incident Metadata:**
- **Primary Category:** AI

**Overview**
This is a test overview paragraph.

**Conclusion**
This is a test conclusion.
'''


@pytest.fixture
def sample_report_text():
    """Fixture providing a sample markdown report."""
    return SAMPLE_REPORT


# =====================================================================
# Tests for _md_section_to_html
# =====================================================================

def test_converts_bold_text():
    """Verify that bold markdown text produces <strong> tags."""
    html = _md_section_to_html("This is **bold text**.")
    assert "<strong>bold text</strong>" in html


def test_converts_bullet_points():
    """Verify that bullet point items produce HTML with bullet symbol."""
    html = _md_section_to_html("- **Key:** Value")
    assert "•" in html
    assert "<strong>Key:</strong> Value" in html


def test_converts_metadata_block():
    """Verify that incident metadata produces a metadata div block."""
    input_text = "**Incident Metadata:**\n- **Category:** AI"
    html = _md_section_to_html(input_text)
    assert '<div class="metadata">' in html
    assert "<strong>Category:</strong> AI" in html


def test_converts_section_headers():
    """Verify that section headers like **Overview** produce <h3>Overview</h3>."""
    html = _md_section_to_html("**Overview**")
    assert "<h3>Overview</h3>" in html


def test_converts_control_box():
    """Verify that proposed control section with bullets produces a control-box div."""
    input_text = (
        "**Proposed Control: Mitigating Threats**\n"
        "- Implement strict access controls.\n"
        "- Monitor audit logs."
    )
    html = _md_section_to_html(input_text)
    assert '<div class="control-box">' in html
    assert "Implement strict access controls." in html
    assert "Monitor audit logs." in html


def test_converts_footnotes():
    """Verify that footnote source reference produces an <a href> tag."""
    input_text = "[1. https://example.com]"
    html = _md_section_to_html(input_text)
    assert '<a href="https://example.com">' in html
    assert "example.com" in html


# =====================================================================
# Tests for convert_to_html_report
# =====================================================================

def test_html_contains_score_badge(sample_report_text):
    """Verify that output HTML contains score-badge class."""
    html = convert_to_html_report(sample_report_text, threat_score=60, date_str="2026-09-14")
    assert "score-badge" in html


def test_html_score_green(sample_report_text):
    """Verify that threat_score=40 applies the score-green class."""
    html = convert_to_html_report(sample_report_text, threat_score=40, date_str="2026-09-14")
    assert "score-green" in html


def test_html_score_orange(sample_report_text):
    """Verify that threat_score=60 applies the score-orange class."""
    html = convert_to_html_report(sample_report_text, threat_score=60, date_str="2026-09-14")
    assert "score-orange" in html


def test_html_score_red(sample_report_text):
    """Verify that threat_score=80 applies the score-red class."""
    html = convert_to_html_report(sample_report_text, threat_score=80, date_str="2026-09-14")
    assert "score-red" in html


def test_html_contains_toc(sample_report_text):
    """Verify that report with incident title produces toc-item containing the title."""
    html = convert_to_html_report(sample_report_text, threat_score=60, date_str="2026-09-14")
    assert "toc-item" in html
    assert "Test Incident Title" in html

    # Also verify with a direct '## Incident Title' report
    custom_report = "## Incident Title\n\n**Overview**\nDetails"
    custom_html = convert_to_html_report(custom_report, threat_score=50, date_str="2026-09-14")
    assert "toc-item" in custom_html
    assert "Incident Title" in custom_html


def test_html_contains_date(sample_report_text):
    """Verify that date_str='2026-09-14' formats and appears as 'September 14, 2026'."""
    html = convert_to_html_report(sample_report_text, threat_score=60, date_str="2026-09-14")
    assert "September 14, 2026" in html
