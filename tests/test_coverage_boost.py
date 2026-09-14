import sys
import os
import json
import pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import news_tracker

def test_update_databases(tmp_path, monkeypatch):
    monkeypatch.setattr(news_tracker, "API_KEY", "dummy")
    
    monkeypatch.setattr(news_tracker, "__file__", os.path.join(str(tmp_path), "news_tracker.py"))

    class MockResponse:
        text = '```json\n{"controls": [{"id": "CTRL-1", "name": "Test", "description": "Desc"}], "incidents": [{"title": "Test Incident", "controls": ["CTRL-1"]}]}\n```'
    
    class MockModels:
        def generate_content(self, *args, **kwargs):
            return MockResponse()
            
    class MockClient:
        def __init__(self, *args, **kwargs):
            self.models = MockModels()
            
    monkeypatch.setattr("google.genai.Client", MockClient)
    
    test_report = '''
## Test Incident Title (2026)

**Incident Metadata:**
- **Primary Category:** AI

**Overview**
Hello

**Proposed Control: Mitigating Threats**
- **I. Governance & Containment (Prevention):** Do something
'''
    # Create the data dir so os.makedirs doesn't complain if it already exists, 
    # actually update_databases creates it.
    news_tracker.update_databases(test_report, "2026-09-14")
    
    controls_path = tmp_path / "data" / "controls_db.json"
    incidents_path = tmp_path / "data" / "incidents_db.json"
    
    assert controls_path.exists()
    assert incidents_path.exists()
    
    with open(controls_path) as f:
        controls = json.load(f)
        assert len(controls) > 0
        
    with open(incidents_path) as f:
        incidents = json.load(f)
        assert len(incidents) > 0

def test_generate_executive_summary_empty():
    assert "Aucun incident" in news_tracker.generate_executive_summary([])

def test_generate_executive_summary_mocked(monkeypatch):
    class MockResponse:
        text = "MOCKED DRAFT"
    
    class MockModels:
        def generate_content(self, *args, **kwargs):
            return MockResponse()
            
    class MockClient:
        def __init__(self, *args, **kwargs):
            self.models = MockModels()
            
    monkeypatch.setattr("google.genai.Client", MockClient)
    
    articles = [{"title": "test", "summary": "test", "link": "test", "source": "test", "published": "test"}]
    res = news_tracker.generate_executive_summary(articles)
    assert res == "MOCKED DRAFT"

def test_verify_and_correct_report_mocked(monkeypatch):
    class MockResponse:
        text = "MOCKED FINAL"
    
    class MockModels:
        def generate_content(self, *args, **kwargs):
            return MockResponse()
            
    class MockClient:
        def __init__(self, *args, **kwargs):
            self.models = MockModels()
            
    monkeypatch.setattr("google.genai.Client", MockClient)
    
    res = news_tracker.verify_and_correct_report("DRAFT", [])
    assert res == "MOCKED FINAL"
