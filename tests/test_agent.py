import pytest
from unittest.mock import patch, MagicMock
from agent import run_workflow, search_web, summarize

def test_run_workflow_empty_topic():
    with pytest.raises(ValueError, match="Please enter a topic."):
        run_workflow("")

def test_run_workflow_whitespace_topic():
    with pytest.raises(ValueError, match="Please enter a topic."):
        run_workflow("   ")

@patch("agent.DDGS")
def test_search_web_returns_results(mock_ddgs):
    mock_instance = MagicMock()
    mock_instance.text.return_value = [
        {"title": "Test Title 1", "body": "Test Body 1"},
        {"title": "Test Title 2", "body": "Test Body 2"},
    ]
    mock_ddgs.return_value.__enter__.return_value = mock_instance
    
    output = search_web("AI news")
    assert "Test Title 1" in output
    assert "Test Body 2" in output

@patch("agent.genai.Client")
def test_summarize_format(mock_client, monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "dummy_key")
    mock_model = MagicMock()
    mock_model.models.generate_content.return_value.text = "- Point 1\n- Point 2\n- Point 3"
    mock_client.return_value = mock_model
    
    result = summarize("AI", "some context")
    assert result.startswith("- Point 1")
    lines = [line for line in result.strip().split("\n") if line.strip()]
    assert len(lines) == 3

def test_summarize_missing_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    with pytest.raises(ValueError, match="GOOGLE_API_KEY environment variable is not set."):
        summarize("AI", "some context")

@patch("agent.summarize")
@patch("agent.search_web")
def test_run_workflow_success(mock_search, mock_summarize):
    mock_search.return_value = "search content"
    mock_summarize.return_value = "- Point 1\n- Point 2\n- Point 3"
    
    result = run_workflow("Agentic AI")
    assert "- Point 1" in result
    mock_search.assert_called_once_with("Agentic AI")