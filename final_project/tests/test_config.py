import os
import pytest
from unittest.mock import patch, mock_open
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config


def test_config_load_from_env() -> None:
    with patch.dict(os.environ, {'API_KEY': 'test-key', 'API_HOST': 'https://test.com/v1'}):
        with patch('os.path.exists', return_value=False):
            config = Config.load()
            assert config.api_key == 'test-key'
            assert config.api_host == 'https://test.com/v1'


def test_config_missing_key() -> None:
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError) as exc_info:
            Config.load()
        assert 'API_KEY не найден' in str(exc_info.value)


def test_config_with_yaml() -> None:
    with patch.dict(os.environ, {'API_KEY': 'test-key', 'API_HOST': 'https://test.com/v1'}):
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch(
                    'yaml.safe_load',
                    return_value={
                        'limit_messages': 10,
                        'limit_chars': 1000,
                        'temperature': 0.5,
                        'system_prompt': 'Test prompt',
                    },
                ):
                    config = Config.load()
                    assert config.limit_messages == 10
                    assert config.limit_chars == 1000
                    assert config.temperature == 0.5
                    assert config.system_prompt == 'Test prompt'
