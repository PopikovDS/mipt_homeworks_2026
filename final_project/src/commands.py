from __future__ import annotations
import os
from .file_processor import FileProcessor
from .chat import Chat


class CommandHandler:
    def __init__(self, chat: Chat) -> None:
        self.chat = chat

    def handle(self, command: str) -> bool:
        if command == '\\q':
            return self._quit()
        elif command == '/reset':
            return self._reset()
        elif command.startswith('/file_chunk'):
            return self._file_chunk(command)
        return False

    def _quit(self) -> bool:
        print('До свидания!')
        return True

    def _reset(self) -> bool:
        self.chat.reset()
        return True

    def _file_chunk(self, command: str) -> bool:
        mode, value, auto_mode = FileProcessor.parse_chunk_command(command)

        mode_names = {
            'paragraph': f'по абзацам (по {value} абзаца(ев) на чанк)',
            'length': f'по символам ({value} символов на чанк)',
        }
        print(f'\nРежим: {mode_names.get(mode, "неизвестный")}')
        if auto_mode:
            print('Автоматический режим: чанки будут обработаны без ожидания Enter\n')

        filepath = input('Введите путь до файла: ').strip()

        if not os.path.exists(filepath):
            print(f"Файл '{filepath}' не найден!")
            return True

        if os.path.getsize(filepath) > 50 * 1024 * 1024:
            size_mb = os.path.getsize(filepath) / 1024 / 1024
            print(f'Файл очень большой ({size_mb:.1f} MB)')
            response = input('Продолжить? (Y/N): ').strip().lower()
            if response != 'y':
                return True

        print('\nЧто нужно сделать для каждого фрагмента?')
        print("   Пример: 'Кратко перескажи текст' или 'Переведи на английский'")
        user_prompt = input('→ ').strip()

        if not user_prompt:
            print('Промпт не может быть пустым!')
            return True

        print('\nНачинаю обработку...\n')
        print('=' * 60)

        try:
            if mode == 'paragraph':
                chunks = FileProcessor.chunk_by_paragraphs(filepath, value if value else 1)
            else:
                chunks = FileProcessor.chunk_by_length(filepath, value if value else 150)
        except Exception as e:
            print(f'Ошибка при чтении файла: {e}')
            return True

        error_msg = 'Ошибка'
        if not chunks or (len(chunks) == 1 and chunks[0].startswith(error_msg)):
            if chunks:
                print(f'{chunks[0]}')
            else:
                print('Файл пуст или не удалось прочитать')
            return True

        print(f'Файл разбит на {len(chunks)} частей\n')

        for i, chunk in enumerate(chunks, 1):
            print(f'\n{"─" * 60}')
            print(f'Чанк {i}/{len(chunks)}')
            print(f'{"─" * 60}')

            preview = chunk[:200] + '...' if len(chunk) > 200 else chunk
            print(f'Содержимое чанка:\n{preview}\n')

            message = f'{user_prompt}\n\nТекст для обработки:\n{chunk}'

            if auto_mode:
                print('Отправляю запрос...\n')
                response: str | None = self.chat.send_message(message)
                if response:
                    print(f'Ответ:\n{response}')
            else:
                input('⏎ Нажмите Enter для обработки этого чанка...')
                print('\nОтправляю запрос...\n')
                response: str | None = self.chat.send_message(message)
                if response:
                    print(f'Ответ:\n{response}')

        print('\n' + '=' * 60)
        print('Обработка файла завершена!')
        return True
