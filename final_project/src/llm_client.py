from openai import OpenAI
from typing import List, Dict, Optional


class LLMClient:
    def __init__(self, api_key: str, api_host: str, temperature: float = 0.7) -> None:
        self.client = OpenAI(base_url=api_host, api_key=api_key)
        self.temperature = temperature

        if 'openrouter' in api_host:
            self.model: str = 'openrouter/meta-llama/llama-3.3-70b-instruct:free'
        elif 'openai' in api_host:
            self.model = 'gpt-3.5-turbo'
        elif 'localhost' in api_host:
            self.model = 'gemma3:270m'
        else:
            self.model = 'gpt-3.5-turbo'

    def send_message(self, messages: List[Dict[str, str]], stream: bool = False) -> Optional[str]:

        try:
            if stream:
                return self._send_streaming(messages)
            else:
                return self._send_sync(messages)
        except Exception as e:
            raise Exception(f'Ошибка при общении с LLM: {e}') from e

    def _send_sync(self, messages: List[Dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.model, messages=messages, temperature=self.temperature
        )
        return str(response.choices[0].message.content)

    def _send_streaming(self, messages: List[Dict[str, str]]) -> str:
        full_response: str = ''
        stream = self.client.chat.completions.create(
            model=self.model, messages=messages, temperature=self.temperature, stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end='', flush=True)
                full_response += content

        print()
        return full_response
