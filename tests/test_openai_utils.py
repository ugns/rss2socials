import pytest
from unittest.mock import patch, MagicMock
from rss2socials.common import openai_utils


# --- validate_openai_env ---
def test_validate_openai_env_ok(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')
    openai_utils.validate_openai_env()  # Should not raise


def test_validate_openai_env_raises(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    with pytest.raises(EnvironmentError):
        openai_utils.validate_openai_env()


# --- generate_summary ---
def make_openai_mock(output_text):
    mock_resp = MagicMock()
    mock_resp.output_text = output_text
    mock_client = MagicMock()
    mock_client.responses.create.return_value = mock_resp
    return mock_client


def make_openai_mock_none_response():
    mock_client = MagicMock()
    mock_client.responses.create.return_value = None
    return mock_client


@patch('rss2socials.common.openai_utils.OpenAI')
@patch('rss2socials.common.openai_utils.grapheme')
def test_generate_summary_within_limit(mock_grapheme, mock_openai, monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')
    mock_openai.return_value = make_openai_mock('Short summary')
    mock_grapheme.length.return_value = 10
    result = openai_utils.generate_summary('Bluesky', 'http://x', max_graphemes=20)
    assert result == 'Short summary'


@patch('rss2socials.common.openai_utils.OpenAI')
@patch('rss2socials.common.openai_utils.grapheme')
def test_generate_summary_content_not_suitable(mock_grapheme, mock_openai, monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')
    mock_openai.return_value = make_openai_mock('Content not suitable for posting')
    result = openai_utils.generate_summary('Bluesky', 'http://x')
    assert result is None


@patch('rss2socials.common.openai_utils.OpenAI')
@patch('rss2socials.common.openai_utils.grapheme')
def test_generate_summary_too_long_truncate(mock_grapheme, mock_openai, monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')
    mock_openai.return_value = make_openai_mock('A' * 50)
    mock_grapheme.length.return_value = 50
    mock_grapheme.graphemes.return_value = ['A'] * 50
    result = openai_utils.generate_summary('Bluesky', 'http://x', max_graphemes=10, max_retries=2)
    assert result == 'A' * 10


@patch('rss2socials.common.openai_utils.OpenAI')
@patch('rss2socials.common.openai_utils.grapheme')
def test_generate_summary_no_output(mock_grapheme, mock_openai, monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')
    mock_openai.return_value = make_openai_mock_none_response()
    mock_grapheme.length.return_value = 0
    mock_grapheme.graphemes.return_value = []
    with pytest.raises(RuntimeError):
        openai_utils.generate_summary('Bluesky', 'http://x', max_graphemes=10, max_retries=1)
