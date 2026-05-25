import re
from pathlib import Path


def expand_file_references(message: str) -> str:
    file_paths = re.findall(r'@::(.*?)::', message)
    for file_path in file_paths:
        try:
            p = Path(file_path)
            if not p.exists():
                print('File not found:', file_path)
                continue
            if not p.is_file():
                print('Not a file:', file_path)
                continue
            if p.stat().st_size > 5 * 1024 * 1024:
                print('File too large:', file_path)
                continue

            with open(p, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                message = message.replace(f'@::{file_path}::', content)

        except Exception as err:
            print(f'Error processing file {file_path}: {err}')

    return message


def _split_by_chars(text: str, chunk_len: int) -> list[str]:
    chunks = []
    for index in range(0, len(text), chunk_len):
        chunks.append(text[index:index + chunk_len])

    return chunks


def _split_by_paragraphs(text: str, paragraph_count: int) -> list[str]:
    paragraphs = text.split('\n\n')
    chunks = []
    for index in range(0, len(paragraphs), paragraph_count):
        chunks.append('\n\n'.join(paragraphs[index:index + paragraph_count]))

    return chunks


def split_into_chunks(text: str, paragraph_count: int = 1,
                      chunk_len: int | None = None) -> list[str]:
    if chunk_len is not None and chunk_len > 0:
        return _split_by_chars(text, chunk_len)

    return _split_by_paragraphs(text, paragraph_count)
