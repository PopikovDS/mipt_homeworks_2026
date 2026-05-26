import os
import re
from typing import List, Tuple


class FileProcessor:

    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5 MB

    @classmethod
    def process_mentions(cls, text: str) -> str:
        pattern: str = r'@::(.*?)::'

        def replace_file(match: re.Match[str]) -> str:
            filepath: str = match.group(1).strip()

            if not os.path.exists(filepath):
                return f'\n[Ошибка: файл {filepath} не найден]\n'

            if os.path.getsize(filepath) > cls.MAX_FILE_SIZE:
                return f'\n[Ошибка: файл {filepath} превышает 5MB]\n'

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content: str = f.read()

                if len(content) > 10000:
                    content = content[:10000] + '\n...[файл обрезан, слишком большой]...'

                return f'\n--- {filepath} ---\n{content}\n--- конец файла ---\n'
            except UnicodeDecodeError:
                return f'\n[Ошибка: файл {filepath} не является текстовым]\n'
            except Exception as e:
                return f'\n[Ошибка при чтении {filepath}: {e}]\n'

        return re.sub(pattern, replace_file, text)

    @classmethod
    def chunk_by_paragraphs(cls, filepath: str, paragraphs: int = 1) -> List[str]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content: str = f.read()
        except Exception as e:
            return [f'Ошибка чтения файла: {e}']

        paras: List[str] = [p for p in content.split('\n\n') if p.strip()]

        if not paras:
            return [content]

        chunks: List[str] = []
        for i in range(0, len(paras), paragraphs):
            chunk: str = '\n\n'.join(paras[i:i + paragraphs])
            chunks.append(chunk)

        return chunks

    @classmethod
    def chunk_by_length(cls, filepath: str, chunk_len: int) -> List[str]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content: str = f.read()
        except Exception as e:
            return [f'Ошибка чтения файла: {e}']

        chunks: List[str] = []
        for i in range(0, len(content), chunk_len):
            chunks.append(content[i:i + chunk_len])

        return chunks

    @classmethod
    def parse_chunk_command(cls, command: str) -> Tuple[str, int, bool]:
        parts: List[str] = command.split()
        auto_mode: bool = '-y' in parts

        parts = [p for p in parts if p != '-y']

        if len(parts) == 1:
            return 'paragraph', 1, auto_mode

        if len(parts) >= 2:
            param: str = parts[1]
            if param.startswith('paragraph='):
                try:
                    num: int = int(param.split('=')[1])
                    if num < 1:
                        num = 1
                    return 'paragraph', num, auto_mode
                except ValueError:
                    return 'paragraph', 1, auto_mode
            elif param.startswith('len='):
                try:
                    length: int = int(param.split('=')[1])
                    if length < 1:
                        length = 150
                    return 'length', length, auto_mode
                except ValueError:
                    return 'length', 150, auto_mode

        return 'paragraph', 1, auto_mode