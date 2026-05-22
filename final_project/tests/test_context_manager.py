import pytest
from src.context_manager import ContextManager


def test_add_message():
    cm = ContextManager(limit_messages=None, limit_chars=None)
    cm.add_message("user", "Hello")
    cm.add_message("assistant", "Hi there!")

    assert len(cm.get_messages()) == 2
    assert cm.get_messages()[0]["role"] == "user"
    assert cm.get_messages()[1]["role"] == "assistant"


def test_limit_messages():
    cm = ContextManager(limit_messages=3, limit_chars=None)

    for i in range(5):
        cm.add_message("user", f"msg{i}")

    messages = cm.get_messages()
    assert len(messages) == 3
    assert messages[0]["content"] == "msg2"
    assert messages[1]["content"] == "msg3"
    assert messages[2]["content"] == "msg4"


def test_limit_chars():
    cm = ContextManager(limit_messages=None, limit_chars=20)

    cm.add_message("user", "x" * 10)
    cm.add_message("user", "y" * 15)  # total 25 > 20

    assert len(cm.get_messages()) == 1
    assert cm.get_messages()[0]["content"] == "y" * 15


def test_system_prompt():
    cm = ContextManager(limit_messages=2, limit_chars=None)
    cm.set_system_prompt("You are helpful")
    cm.add_message("user", "msg1")
    cm.add_message("user", "msg2")
    cm.add_message("user", "msg3")  # должно удалить msg1

    messages = cm.get_messages()
    assert len(messages) == 3  # system + msg2 + msg3
    assert messages[0]["role"] == "system"
    assert messages[1]["content"] == "msg2"
    assert messages[2]["content"] == "msg3"


def test_clear():
    cm = ContextManager(limit_messages=None, limit_chars=None)
    cm.add_message("user", "test")
    cm.add_message("assistant", "response")

    cm.clear()

    assert len(cm.get_messages()) == 0