from chat import Chat
from config import ConfigError


def start_chatting() -> None:
    chat = Chat()
    chat.run()


def main() -> None:
    try:
        start_chatting()
    except ConfigError as err:
        print(f'Configuration error: {err}')
    except Exception as err:
        print(f'Unexpected error: {err}')
        raise


if __name__ == '__main__':
    main()
