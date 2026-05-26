import os
import yaml
from dataclasses import dataclass
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    api_key: str
    api_host: str
    limit_messages: Optional[int]
    limit_chars: Optional[int]
    temperature: float
    system_prompt: Optional[str]

    @classmethod
    def load(cls) -> 'Config':
        api_key: Optional[str] = os.getenv('API_KEY')
        api_host: Optional[str] = os.getenv('API_HOST')

        if not api_key:
            raise ValueError(
                'API_KEY не найден!\n'
                'Создайте файл .env с содержимым:\n'
                'API_KEY=sk-proj-ваш_ключ\n'
                'API_HOST=https://api.openai.com/v1'
            )

        if not api_host:
            raise ValueError(
                'API_HOST не найден!\n'
                'Создайте файл .env с содержимым:\n'
                'API_KEY=sk-proj-ваш_ключ\n'
                'API_HOST=https://api.openai.com/v1'
            )

        yaml_config: Dict[str, Any] = {}
        if os.path.exists('config.yaml'):
            try:
                with open('config.yaml', 'r', encoding='utf-8') as f:
                    yaml_config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f'Ошибка чтения config.yaml: {e}')

        temperature: float = yaml_config.get('temperature', 0.7)
        if not 0 <= temperature <= 1:
            print(f'Температура {temperature} вне диапазона 0-1, установлена 0.7')
            temperature = 0.7

        return cls(
            api_key=api_key,
            api_host=api_host.rstrip('/'),
            limit_messages=yaml_config.get('limit_messages'),
            limit_chars=yaml_config.get('limit_chars'),
            temperature=float(temperature),
            system_prompt=yaml_config.get('system_prompt')
        )