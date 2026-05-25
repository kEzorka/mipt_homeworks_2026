# Итоговый проект "GigaVibeMiptCode"

Консольное приложение-чат для общения с LLM

## Требования

- Python 3.10+
- [Ollama](https://ollama.com) или любой OpenAI-совместимый провайдер

## Установка

```bash
pip install openai pyyaml
```

## Конфигурация

Можно создать файл `config.yaml` в корне проекта. Пример есть в `config.yaml.example`.

Или задать переменные окружения, которые имеют приоритет над `config.yaml`:

```bash
export API_KEY=your_api_key
export API_HOST=http://localhost:11434/v1/
export MODEL=qwen3.5:4b
export LIMIT_MESSAGE=20
export LIMIT_CHARS=2000
export TEMPERATURE=0.7
```

## Запуск

```bash
python main.py
```

## Команды

| Команда                  | Описание                                                   |
|--------------------------|------------------------------------------------------------|
| `\q`                     | Выйти из программы                                         |
| `/reset`                 | Очистить историю сообщений и экран                         |
| `/file_chunk`            | Обработать файл по частям                                  |
| `/file_chunk paragraph=N`| Разбить по N абзацев                                       |
| `/file_chunk len=N`      | Разбить по N символов                                      |
| `/file_chunk -y`         | Обработать все чанки без подтверждения                     |
| `/stop`                  | Завершить обработку файла **(только внутри file_chunk)**   |
| `@::путь/к/файлу::`      | Вставить содержимое файла в сообщение                      |
