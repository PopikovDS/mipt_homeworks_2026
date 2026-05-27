import os
from typing import Optional, Dict

from src.config import Config
from src.context_manager import ContextManager
from src.llm_client import LLMClient
from src.file_processor import FileProcessor


class Chat:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.context = ContextManager(config.limit_messages, config.limit_chars)
        self.llm = LLMClient(config.api_key, config.api_host, config.temperature)

        if config.system_prompt:
            self.context.set_system_prompt(config.system_prompt)

    def send_message(self, user_input: str, stream: bool = False) -> Optional[str]:
        processed_input = FileProcessor.process_mentions(user_input)

        self.context.add_message('user', processed_input)

        try:
            response = self.llm.send_message(self.context.get_messages(), stream=stream)

            if response:
                self.context.add_message('assistant', response)

            return response
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f'\n{e}')
            return None

    def reset(self) -> None:
        self.context.clear()
        self._clear_screen()
        print('История чата очищена! Начинаем новый диалог.\n')

    def _clear_screen(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_stats(self) -> Dict[str, int]:
        stats = self.context.get_stats()
        return stats