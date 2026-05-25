from dataclasses import dataclass
import pathlib
import os
import yaml

BASE_DIR = pathlib.Path(__file__).parent
CONFIG_PATH = BASE_DIR / 'config.yaml'


class ConfigError(Exception):
    pass


@dataclass
class Config:
    api_key: str
    api_host: str
    model: str
    limit_message: int
    limit_chars: int
    temperature: float
    system_prompt: str | None


def _load_yaml_config() -> dict[str, str]:
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
    except yaml.YAMLError as err:
        raise ConfigError('Error loading YAML configuration') from err

    return {}


def _load_env_config(yaml_config: dict[str, str]) -> Config:
    try:
        return Config(
            api_key=os.environ.get('API_KEY') or yaml_config.get('api_key', ''),
            api_host=os.environ.get('API_HOST') or yaml_config.get('api_host', ''),
            model=os.environ.get('MODEL') or yaml_config.get('model', ''),
            limit_message=int(
                os.environ.get('LIMIT_MESSAGE') or yaml_config.get('limit_message', '20')
            ),
            limit_chars=int(
                os.environ.get('LIMIT_CHARS') or yaml_config.get('limit_chars', '2000')
            ),
            temperature=float(
                os.environ.get('TEMPERATURE') or yaml_config.get('temperature', '0.7')
            ),
            system_prompt=os.environ.get('SYSTEM_PROMPT') or yaml_config.get('system_prompt'),
        )
    except (ValueError, TypeError) as err:
        raise ConfigError('Error loading configuration') from err


def load_config() -> Config:
    yaml_config = _load_yaml_config()
    config = _load_env_config(yaml_config)

    if not config.api_key or not config.api_host or not config.model:
        raise ConfigError(
            'API_KEY, API_HOST, and MODEL must be set in '
            'either environment variables or config.yaml'
        )

    if config.temperature < 0 or config.temperature > 1:
        raise ConfigError('TEMPERATURE must be between 0 and 1')

    return config
