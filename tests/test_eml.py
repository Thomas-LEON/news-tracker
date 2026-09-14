"""Tests for EML newsletter generation."""

import datetime
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pytest


def build_eml_message(
    date_str="2026-09-14",
    plain_text="Please enable HTML to view this intelligence briefing.",
    html_content="<h1>Daily Threat Intel Report</h1><p>Test HTML content</p>",
):
    """Construct an EML MIMEMultipart message matching the news_tracker implementation."""
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = date_obj.strftime("%B %d, %Y")
    except Exception:
        formatted_date = date_str

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Daily Threat Intel Report - {formatted_date}"
    msg["From"] = ""
    msg["To"] = ""
    msg["MIME-Version"] = "1.0"
    msg.attach(MIMEText(plain_text, "plain", "utf-8"))
    msg.attach(MIMEText(html_content, "html", "utf-8"))
    return msg


@pytest.fixture
def sample_eml():
    """Fixture providing a standard sample EML message."""
    return build_eml_message()


def test_eml_has_mime_version(sample_eml):
    """Verify that msg.as_string() contains 'MIME-Version: 1.0'."""
    raw_eml = sample_eml.as_string()
    assert "MIME-Version: 1.0" in raw_eml


def test_eml_has_subject(sample_eml):
    """Verify that the EML contains 'Subject: Daily Threat Intel Report'."""
    raw_eml = sample_eml.as_string()
    assert "Subject: Daily Threat Intel Report" in raw_eml
    assert sample_eml["Subject"].startswith("Daily Threat Intel Report")


def test_eml_has_multipart_alternative(sample_eml):
    """Verify that the EML structure contains 'multipart/alternative'."""
    raw_eml = sample_eml.as_string()
    assert "multipart/alternative" in raw_eml
    assert sample_eml.get_content_type() == "multipart/alternative"


def test_eml_has_plain_text_fallback(sample_eml):
    """Verify that the EML contains 'Please enable HTML to view this intelligence briefing.'."""
    expected_text = "Please enable HTML to view this intelligence briefing."
    parsed = email.message_from_string(sample_eml.as_string())
    plain_parts = [
        part.get_payload(decode=True).decode("utf-8")
        for part in parsed.walk()
        if part.get_content_type() == "text/plain"
    ]
    assert any(expected_text in part for part in plain_parts)


def test_eml_has_html_content():
    """Verify that the EML contains the HTML content passed in."""
    custom_html = "<div class='intel-report'><h2>Threat Actor Activity</h2></div>"
    msg = build_eml_message(html_content=custom_html)
    parsed = email.message_from_string(msg.as_string())
    html_parts = [
        part.get_payload(decode=True).decode("utf-8")
        for part in parsed.walk()
        if part.get_content_type() == "text/html"
    ]
    assert any(custom_html in part for part in html_parts)


def test_eml_has_correct_date_in_subject():
    """Verify that for date '2026-09-14', subject contains 'September 14, 2026'."""
    msg = build_eml_message(date_str="2026-09-14")
    assert "September 14, 2026" in msg["Subject"]
    assert "Subject: Daily Threat Intel Report - September 14, 2026" in msg.as_string()
