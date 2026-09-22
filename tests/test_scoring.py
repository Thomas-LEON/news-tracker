import re

# Regex used to extract auditable metrics from LLM draft report
METRICS_PATTERN = r"\*\(\s*Auditable Metrics\s*-\s*Threat Capability:\s*(\d+)/10\s*\|\s*Event Frequency:\s*(\d+)/10\s*\|\s*Business Impact:\s*(\d+)/10\s*\)\*"


def calculate_score(tc: int, ef: int, bi: int) -> int:
    """Calculate threat score based on TC, EF, and BI metrics, capped at 100."""
    return min(int((tc + ef + bi) * 3.33), 100)


def get_color(score: int) -> str:
    """Determine color classification based on score thresholds."""
    if score <= 50:
        return "green"
    elif score <= 75:
        return "orange"
    else:
        return "red"


def extract_and_calculate_score(text: str) -> int:
    """Extract metrics from text using regex and calculate threat score, defaulting to 0 if unmatched."""
    match = re.search(METRICS_PATTERN, text, re.IGNORECASE)
    if match:
        tc = int(match.group(1))
        ef = int(match.group(2))
        bi = int(match.group(3))
        return calculate_score(tc, ef, bi)
    return 0


def test_score_calculation_basic():
    """TC=5, EF=6, BI=7 -> score = int(18*3.33) = 59"""
    score = calculate_score(5, 6, 7)
    assert score == int(18 * 3.33)
    assert score == 59


def test_score_calculation_low():
    """TC=2, EF=2, BI=2 -> score = int(6*3.33) = 19"""
    score = calculate_score(2, 2, 2)
    assert score == int(6 * 3.33)
    assert score == 19


def test_score_calculation_high():
    """TC=10, EF=10, BI=10 -> score = min(int(30*3.33), 100) = 99"""
    score = calculate_score(10, 10, 10)
    assert score == min(int(30 * 3.33), 100)
    assert score == 99


def test_score_calculation_cap_at_100():
    """Verify score never exceeds 100 even with high input metrics."""
    assert calculate_score(11, 11, 11) == 100
    assert calculate_score(10, 10, 11) == 100
    assert calculate_score(15, 15, 15) == 100
    assert calculate_score(100, 100, 100) == 100
    for val in range(31, 50):
        assert min(int(val * 3.33), 100) <= 100


def test_color_green():
    """Score 19 -> green"""
    assert get_color(19) == "green"


def test_color_orange():
    """Score 59 -> orange"""
    assert get_color(59) == "orange"


def test_color_red():
    """Score 80 -> red"""
    assert get_color(80) == "red"


def test_color_boundary_50():
    """Score exactly 50 -> green"""
    assert get_color(50) == "green"


def test_color_boundary_75():
    """Score exactly 75 -> orange"""
    assert get_color(75) == "orange"


def test_regex_extraction():
    """Test that regex correctly extracts TC, EF, BI from sample string."""
    sample = "*(Auditable Metrics - Threat Capability: 5/10 | Event Frequency: 6/10 | Business Impact: 7/10)*"
    match = re.search(METRICS_PATTERN, sample, re.IGNORECASE)
    assert match is not None
    tc = int(match.group(1))
    ef = int(match.group(2))
    bi = int(match.group(3))
    assert tc == 5
    assert ef == 6
    assert bi == 7
    assert calculate_score(tc, ef, bi) == 59


def test_regex_no_match():
    """Test that when string doesn't match, score defaults to 0."""
    invalid_sample = "Report with missing or malformed metrics line."
    assert extract_and_calculate_score(invalid_sample) == 0
