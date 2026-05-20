import os
from enum import StrEnum
from config import load_config
from openai import OpenAI
from context import Context
from pathlib import Path
from file_handler import expand_file_references, split_into_chunks
import llm_client

positive_int = int | None


class Command(StrEnum):
    QUIT = '\\q'
    RESET = '/reset'
    FILE_CHUNK_START = '/file_chunk'
    FILE_CHUNK_CANCEL = '/stop'


class Chat:
    def __init__(self) -> None:
        self.config = load_config()

        self.client = OpenAI(api_key=self.config.api_key, base_url=self.config.api_host)
        self.context = Context(system_prompt=self.config.system_prompt)

    def run(self) -> None:
        try:
            self._chat_loop()
        except (KeyboardInterrupt, EOFError):
            print()
            self._handle_quit()

    def _chat_loop(self) -> None:
        while True:
            user_content = self._get_input()

            match user_content:
                case Command.QUIT:
                    self._handle_quit()
                    break
                case Command.RESET:
                    self._handle_reset()
                    continue
                case _ if user_content.startswith(Command.FILE_CHUNK_START):
                    parameters = self._parse_file_chunk_args(user_content)
                    self._handle_file_chunk(*parameters)
                case _:
                    self._handle_add_message('user', user_content)
                    self._send_and_print_response()

    def _get_input(self) -> str:
        while True:
            print('❯ ', end='', flush=True)
            user_content = expand_file_references(input())
            if len(user_content) > self.config.limit_chars:
                print(f'Input too long. Max {self.config.limit_chars} chars.')
                continue
            return user_content

    def _handle_add_message(self, role: str, content: str) -> None:
        self.context.add_message(role, content)
        self.context.trim(self.config.limit_message, self.config.limit_chars)

    def _send_and_print_response(self) -> None:
        try:
            print('◆', end=' ', flush=True)
            response = llm_client.send(
                model=self.config.model,
                messages=self.context.messages,
                client=self.client,
                temperature=self.config.temperature,
                on_token=lambda token: print(token, end='', flush=True)
            )
            print()
            self._handle_add_message('assistant', response)

        except KeyboardInterrupt:
            print('\nRequest cancelled.')

        except llm_client.LLMError as err:
            print(f'LLM error: {err}')

    def _handle_quit(self) -> None:
        print('Goodbye!')

    def _handle_reset(self) -> None:
        self.context = Context(system_prompt=self.config.system_prompt)
        os.system('cls' if os.name == 'nt' else 'clear')

    def _handle_file_chunk(self, paragraph_count: int,
                           chunk_len: positive_int, auto_confirm: bool) -> None:
        message = self._read_file_for_chunking()
        if message is None:
            return

        chunks: list[str] = split_into_chunks(message, paragraph_count, chunk_len)
        print('File content loaded. What to do with chunks?')

        user_prompt = self._get_input()
        self._handle_chunking_processing(user_prompt, chunks, auto_confirm)
        print('Quitting file chunking mode.')

    def _read_file_for_chunking(self) -> str | None:
        print(f'Tip: enter "{Command.FILE_CHUNK_CANCEL}" to cancel')

        while True:
            print('Enter file path: ')
            file_path = self._get_input()

            if file_path == Command.FILE_CHUNK_CANCEL:
                return None

            try:
                p = Path(file_path)
                if not p.exists():
                    print('File not found:', file_path)
                    continue
                if not p.is_file():
                    print('Not a file:', file_path)
                    continue

                with open(p, 'r', encoding='utf-8', errors='replace') as f:
                    return f.read()

            except Exception as err:
                print(f'Error processing file {file_path}: {err}')

    def _handle_chunking_processing(
        self, user_prompt: str, chunks: list[str], auto_confirm: bool
    ) -> None:
        print('Processing...')
        self._handle_add_message('user', user_prompt)

        for index, chunk in enumerate(chunks):
            self._handle_add_message('user', chunk)
            self._send_and_print_response()
            if index != len(chunks) - 1 and not auto_confirm:
                user_content = self._get_input()
                if user_content == Command.FILE_CHUNK_CANCEL:
                    break
                if user_content:
                    print('Your content will be ignored, since the file is being processed.')

        print('File processing completed.')

    def _parse_file_chunk_args(self, command: str) -> tuple[int, positive_int, bool]:
        args = command.split()[1:]

        paragraph_count = 1
        chunk_len: positive_int = None
        auto_confirm = False
        for arg in args:
            if arg.startswith('paragraph='):
                paragraph_count = self._get_paragraphs_value(arg)

            elif arg.startswith('len='):
                chunk_len = self._get_chunk_len_value(arg)

            elif arg == '-y':
                auto_confirm = True
            else:
                print(f'Unknown argument: {arg}')

        return paragraph_count, chunk_len, auto_confirm

    def _get_paragraphs_value(self, arg: str) -> int:
        paragraph_count = 1
        try:
            paragraph_count = int(arg.split('=')[1])

        except ValueError:
            print('Invalid paragraphs value. Using default 1.')

        if paragraph_count < 1:
            print('paragraph_count must be a positive integer. Using default 1.')
            paragraph_count = 1

        return paragraph_count

    def _get_chunk_len_value(self, arg: str) -> positive_int:
        chunk_len = None
        try:
            chunk_len = int(arg.split('=')[1])

            if chunk_len < 0:
                print('chunk_len must be a positive integer. Using default None.')
                chunk_len = None

        except ValueError:
            print('Invalid chunk_len value. Using default None.')

        return chunk_len
