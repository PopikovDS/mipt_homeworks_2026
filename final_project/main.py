import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.chat import Chat
from src.commands import CommandHandler


def print_welcome():
    print("=" * 60)
    print("GigaVibeMiptCode - Ваш персональный ИИ-помощник")
    print("=" * 60)
    print("\nКоманды:")
    print("   /reset                         - очистить историю чата")
    print("   \\q                             - выход из программы")
    print("   @::file.txt::                  - прикрепить текстовый файл")
    print("   /file_chunk                    - обработать большой файл по частям")
    print("   /file_chunk -y                 - автоматический режим")
    print("   /file_chunk paragraph=3        - по 3 абзаца на чанк")
    print("   /file_chunk len=500            - по 500 символов на чанк")
    print("\nСоветы:")
    print("   • Нажмите Ctrl+C во время ответа модели, чтобы прервать запрос")
    print("   • Используйте @::main.py:: для анализа кода")
    print("\n" + "=" * 60 + "\n")


def main():
    print_welcome()

    try:
        config = Config.load()
    except ValueError as e:
        print(f"{e}")
        return
    except Exception as e:
        print(f"Неожиданная ошибка при загрузке конфигурации: {e}")
        return

    try:
        chat = Chat(config)
        command_handler = CommandHandler(chat)
    except Exception as e:
        print(f"Ошибка при инициализации чата: {e}")
        return

    print("Текущие настройки:")
    print(f"   • Хост API: {config.api_host}")
    print(f"   • Лимит сообщений: {config.limit_messages or '∞'}")
    print(f"   • Лимит символов: {config.limit_chars or '∞'}")
    print(f"   • Температура: {config.temperature}")
    print()

    print("Готов к общению! Введите сообщение или команду.\n")

    while True:
        try:
            user_input = input("👤 Вы: ").strip()

            if not user_input:
                continue

            if command_handler.handle(user_input):
                if user_input == '\\q':
                    break
                continue

            print("\nБот думает... (Ctrl+C для отмены)\n")

            try:
                response = chat.send_message(user_input, stream=False)
                if response:
                    print(f"\nБот: {response}")

                stats = chat.get_stats()
                if stats['message_count'] > 5:  # Не показываем для коротких диалогов
                    print(f"\n[Статистика: {stats['message_count']} сообщений, {stats['total_chars']} символов]")

            except KeyboardInterrupt:
                print("\n\nЗапрос прерван! Возвращаемся к вводу.\n")
                continue

        except KeyboardInterrupt:
            print("\n\nДо свидания!")
            break
        except EOFError:
            print("\n\nДо свидания!")
            break
        except Exception as e:
            print(f"\nНеожиданная ошибка: {e}")
            print("Попробуйте еще раз или введите \\q для выхода\n")


if __name__ == "__main__":
    main()