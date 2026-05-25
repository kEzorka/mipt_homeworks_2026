from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
    ChatCompletionAssistantMessageParam,
)


class ContextError(Exception):
    pass


class Context:
    def __init__(self, system_prompt: str | None = None) -> None:
        self.messages: list[ChatCompletionMessageParam] = []
        if system_prompt is not None:
            self.add_system_message(system_prompt)

    def add_system_message(self, content: str) -> None:
        self.messages.append(
            ChatCompletionSystemMessageParam({'role': 'system', 'content': content})
        )

    def add_message(self, role: str, content: str) -> None:
        if role == 'user':
            self.messages.append(
                ChatCompletionUserMessageParam({'role': 'user', 'content': content})
            )
        elif role == 'assistant':
            self.messages.append(
                ChatCompletionAssistantMessageParam({'role': 'assistant', 'content': content})
            )
        else:
            raise ContextError('Invalid message role')

    def trim(self, limit_message: int, limit_chars: int) -> None:
        if not self.messages:
            return
        has_system_message = bool(self.messages[0]['role'] == 'system')

        while self._is_messages_over_limits(limit_message, limit_chars):
            if self._cut_messages_to_fit_char_limit(limit_chars, has_system_message):
                break

            if has_system_message:
                self.messages.pop(1)
            else:
                self.messages.pop(0)

    def _is_messages_over_limits(self, limit_message: int, limit_chars: int) -> bool:
        if len(self.messages) > limit_message:
            return True

        return (
            sum(len(m['content']) if isinstance(m['content'], str) else 0 for m in self.messages)
            > limit_chars
        )

    def _cut_messages_to_fit_char_limit(self, limit_chars: int, has_system_message: bool) -> bool:
        if not has_system_message and len(self.messages) == 1:
            self.messages[0]['content'] = str(self.messages[0]['content'])[-limit_chars:]
            return True

        if has_system_message and len(self.messages) == 1:
            raise ContextError('Cannot trim context: only system message left')

        if has_system_message and len(self.messages) == 2:
            system_msg_len = len(str(self.messages[0]['content']))
            self.messages[1]['content'] = (str(self.messages[1]['content'])
                                           [-limit_chars + system_msg_len:])
            return True

        return False
