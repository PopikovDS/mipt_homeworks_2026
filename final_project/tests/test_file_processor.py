import pytest
from unittest.mock import patch, mock_open
from src.file_processor import FileProcessor


def test_process_mentions_file_not_found():
    text = "Check @::nonexistent.txt::"
    result = FileProcessor.process_mentions(text)

    assert "не найден" in result


def test_process_mentions_valid_file():
    mock_content = "print('Hello World')"

    with patch('os.path.exists', return_value=True):
        with patch('os.path.getsize', return_value=100):
            with patch('builtins.open', mock_open(read_data=mock_content)):
                result = FileProcessor.process_mentions("Look @::test.py::")

                assert "test.py" in result
                assert "print('Hello World')" in result


def test_file_size_limit():
    with patch('os.path.exists', return_value=True):
        with patch('os.path.getsize', return_value=6 * 1024 * 1024):  # 6 MB > 5 MB
            result = FileProcessor.process_mentions("@::bigfile.txt::")
            assert "превышает 5MB" in result


def test_chunk_by_paragraphs():
    mock_content = "First paragraph\n\nSecond paragraph\n\nThird paragraph"

    with patch('builtins.open', mock_open(read_data=mock_content)):
        chunks = FileProcessor.chunk_by_paragraphs("test.txt", paragraphs=1)

        assert len(chunks) == 3
        assert "First paragraph" in chunks[0]
        assert "Second paragraph" in chunks[1]
        assert "Third paragraph" in chunks[2]


def test_chunk_by_length():
    mock_content = "1234567890" * 10  # 100 chars

    with patch('builtins.open', mock_open(read_data=mock_content)):
        chunks = FileProcessor.chunk_by_length("test.txt", chunk_len=30)

        assert len(chunks) == 4
        assert len(chunks[0]) <= 30


def test_parse_chunk_command():
    mode, value, auto = FileProcessor.parse_chunk_command("/file_chunk")
    assert mode == 'paragraph'
    assert value == 1
    assert auto is False

    mode, value, auto = FileProcessor.parse_chunk_command("/file_chunk paragraph=5")
    assert mode == 'paragraph'
    assert value == 5
    assert auto is False

    mode, value, auto = FileProcessor.parse_chunk_command("/file_chunk paragraph=3 -y")
    assert mode == 'paragraph'
    assert value == 3
    assert auto is True

    mode, value, auto = FileProcessor.parse_chunk_command("/file_chunk len=500")
    assert mode == 'length'
    assert value == 500
    assert auto is False
