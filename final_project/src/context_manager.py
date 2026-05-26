from typing import List, Dict, Optional


class ContextManager:

    def __init__(self, limit_messages: Optional[int], limit_chars: Optional[int]) -> None:
        self.messages: List[Dict[str, str]] = []
        self.limit_messages = limit_messages
        self.limit_chars = limit_chars
        self._system_message: Optional[Dict[str, str]] = None

    def set_system_prompt(self, system_prompt: str) -> None:
        self._system_message = {'role': 'system', 'content': system_prompt}
        self._rebuild_messages()

    def add_message(self, role: str, content: str) -> None:
        self.messages.append({'role': role, 'content': content})
        self._apply_limits()

    def _rebuild_messages(self) -> None:
        if self._system_message:
            self.messages = [m for m in self.messages if m['role'] != 'system']
            self.messages = [self._system_message] + self.messages
        self._apply_limits()

    def _apply_limits(self) -> None:
        if self.limit_messages:
            if self._system_message and self.messages and self.messages[0]['role'] == 'system':
                system = self.messages[0]
                others = self.messages[1:]
                if len(others) > self.limit_messages:
                    others = others[-self.limit_messages:]
                self.messages = [system] + others
            else:
                if len(self.messages) > self.limit_messages:
                    self.messages = self.messages[-self.limit_messages:]

        if self.limit_chars:
            total_chars = sum(len(m.get('content', '')) for m in self.messages)
            while total_chars > self.limit_chars and len(self.messages) > 1:
                if self._system_message and self.messages[0]['role'] == 'system':
                    if len(self.messages) > 1:
                        removed = self.messages.pop(1)
                    else:
                        break
                else:
                    removed = self.messages.pop(0)
                total_chars -= len(removed.get('content', ''))

            for _i, msg in enumerate(self.messages):
                if len(msg.get('content', '')) > self.limit_chars:
                    msg['content'] = (
                        msg['content'][:self.limit_chars] + '...[обрезано]'
                    )

    def get_messages(self) -> List[Dict[str, str]]:
        return self.messages.copy()

    def clear(self) -> None:
        if self._system_message:
            self.messages = [self._system_message]
        else:
            self.messages = []

    def get_stats(self) -> Dict[str, int]:
        return {
            'message_count': len(self.messages),
            'total_chars': sum(len(m.get('content', '')) for m in self.messages)
        }