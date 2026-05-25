from openai import OpenAI, OpenAIError
from openai.types.chat import ChatCompletionMessageParam
from typing import Callable


class LLMError(Exception):
    pass


def send(
    model: str, temperature: float,
    messages: list[ChatCompletionMessageParam], client: OpenAI,
    on_token: Callable[[str], None] | None = None
) -> str:
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        result = ''
        for chunk in stream:
            token = chunk.choices[0].delta.content or ''
            if on_token:
                on_token(token)
            result += token
        return result

    except OpenAIError as err:
        raise LLMError(f'API error: {err}') from err
