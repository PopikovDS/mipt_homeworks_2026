from src.context_manager import ContextManager


def test_add_message() -> None:
    cm = ContextManager(limit_messages=None, limit_chars=None)
    cm.add_message('user', 'Hello')
    cm.add_message('assistant', 'Hi there!')

    assert len(cm.get_messages()) == 2
    assert cm.get_messages()[0]['role'] == 'user'
    assert cm.get_messages()[1]['role'] == 'assistant'


def test_limit_messages() -> None:
    cm = ContextManager(limit_messages=3, limit_chars=None)

    for i in range(5):
        cm.add_message('user', f'msg{i}')

    messages = cm.get_messages()
    assert len(messages) == 3
    assert messages[0]['content'] == 'msg2'
    assert messages[1]['content'] == 'msg3'
    assert messages[2]['content'] == 'msg4'


def test_limit_chars() -> None:
    cm = ContextManager(limit_messages=None, limit_chars=20)

    cm.add_message('user', 'x' * 10)
    cm.add_message('user', 'y' * 15)

    assert len(cm.get_messages()) == 1
    assert cm.get_messages()[0]['content'] == 'y' * 15


def test_system_prompt() -> None:
    cm = ContextManager(limit_messages=2, limit_chars=None)
    cm.set_system_prompt('You are helpful')
    cm.add_message('user', 'msg1')
    cm.add_message('user', 'msg2')
    cm.add_message('user', 'msg3')

    messages = cm.get_messages()
    assert len(messages) == 3
    assert messages[0]['role'] == 'system'
    assert messages[1]['content'] == 'msg2'
    assert messages[2]['content'] == 'msg3'


def test_clear() -> None:
    cm = ContextManager(limit_messages=None, limit_chars=None)
    cm.add_message('user', 'test')
    cm.add_message('assistant', 'response')

    cm.clear()

    assert len(cm.get_messages()) == 0