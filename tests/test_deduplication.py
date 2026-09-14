import datetime
from pathlib import Path
import sys
import pytest

# Ensure repository root is in sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import news_tracker
from news_tracker import get_previously_covered_incidents


@pytest.fixture
def tracker_env(tmp_path, monkeypatch):
    """
    Configure news_tracker.__file__ to locate reports in tmp_path.
    Returns tmp_path as the base directory.
    """
    fake_module_file = tmp_path / "news_tracker.py"
    monkeypatch.setattr(news_tracker, "__file__", str(fake_module_file))
    return tmp_path


def create_daily_report(base_dir: Path, days_ago: int, content: str) -> Path:
    """Helper to create a Daily_Threat_Intel_<date>.md report file in reports/."""
    reports_dir = base_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    target_date = (datetime.datetime.now() - datetime.timedelta(days=days_ago)).strftime("%Y-%m-%d")
    report_file = reports_dir / f"Daily_Threat_Intel_{target_date}.md"
    report_file.write_text(content, encoding="utf-8")
    return report_file


def test_no_reports_dir(tracker_env):
    """When reports/ directory does not exist, returns an empty list."""
    reports_dir = tracker_env / "reports"
    assert not reports_dir.exists()
    result = get_previously_covered_incidents()
    assert result == []


def test_reads_yesterday_report(tracker_env):
    """Create a fake .md file for yesterday with two H2 titles and verify both are returned."""
    content = (
        "# Daily Threat Intelligence Report\n\n"
        "## Incident Title A\n"
        "Summary of incident A.\n\n"
        "## Incident Title B\n"
        "Summary of incident B.\n"
    )
    create_daily_report(tracker_env, days_ago=1, content=content)

    result = get_previously_covered_incidents()
    assert sorted(result) == ["Incident Title A", "Incident Title B"]


def test_reads_multiple_days(tracker_env):
    """Create fake .md files for the last 3 days and verify all titles from all 3 are returned."""
    create_daily_report(tracker_env, days_ago=1, content="## Incident Day 1\nDetails day 1.")
    create_daily_report(tracker_env, days_ago=2, content="## Incident Day 2\nDetails day 2.")
    create_daily_report(tracker_env, days_ago=3, content="## Incident Day 3\nDetails day 3.")

    result = get_previously_covered_incidents(days=3)
    assert set(result) == {"Incident Day 1", "Incident Day 2", "Incident Day 3"}


def test_deduplication(tracker_env):
    """Verify that the same title across 2 different days appears only once."""
    create_daily_report(
        tracker_env,
        days_ago=1,
        content="## Ransomware Outbreak\n## Phishing Campaign\n",
    )
    create_daily_report(
        tracker_env,
        days_ago=2,
        content="## Ransomware Outbreak\n## Zero-Day Exploit\n",
    )

    result = get_previously_covered_incidents(days=3)
    assert sorted(result) == [
        "Phishing Campaign",
        "Ransomware Outbreak",
        "Zero-Day Exploit",
    ]
    # Verify strict deduplication: title count should be 1
    assert result.count("Ransomware Outbreak") == 1


def test_ignores_non_h2_headers(tracker_env):
    """Lines with # Main Title, ### Sub, bullet points, or plain text should not be picked up."""
    content = (
        "# Main Title (H1)\n"
        "### Sub Heading (H3)\n"
        "#### Sub Sub Heading (H4)\n"
        "- ## Not a header (bullet)\n"
        "Regular paragraph text with ## inline markdown.\n"
        "## Valid Incident Title\n"
        "##    Incident With Whitespace   \n"
    )
    create_daily_report(tracker_env, days_ago=1, content=content)

    result = get_previously_covered_incidents()
    assert sorted(result) == ["Incident With Whitespace", "Valid Incident Title"]


@pytest.mark.parametrize(
    "days_param,expected_titles",
    [
        (1, {"Incident Day 1"}),
        (2, {"Incident Day 1", "Incident Day 2"}),
        (3, {"Incident Day 1", "Incident Day 2", "Incident Day 3"}),
    ],
)
def test_custom_days_parameter(tracker_env, days_param, expected_titles):
    """Test custom days parameter ensures only reports within the specified window are read."""
    create_daily_report(tracker_env, days_ago=1, content="## Incident Day 1\n")
    create_daily_report(tracker_env, days_ago=2, content="## Incident Day 2\n")
    create_daily_report(tracker_env, days_ago=3, content="## Incident Day 3\n")
    create_daily_report(tracker_env, days_ago=4, content="## Incident Day 4\n")

    result = get_previously_covered_incidents(days=days_param)
    assert set(result) == expected_titles


def test_custom_days_parameter_days_1_only_reads_yesterday(tracker_env):
    """Explicit test checking that days=1 only reads yesterday's report."""
    create_daily_report(tracker_env, days_ago=1, content="## Yesterday Incident\n")
    create_daily_report(tracker_env, days_ago=2, content="## Older Incident\n")

    result = get_previously_covered_incidents(days=1)
    assert result == ["Yesterday Incident"]


def test_handles_missing_file_within_range(tracker_env):
    """If a report file is missing for one of the days in the range, the others are still parsed."""
    create_daily_report(tracker_env, days_ago=1, content="## Day 1 Incident\n")
    # Day 2 is deliberately missing
    create_daily_report(tracker_env, days_ago=3, content="## Day 3 Incident\n")

    result = get_previously_covered_incidents(days=3)
    assert set(result) == {"Day 1 Incident", "Day 3 Incident"}
