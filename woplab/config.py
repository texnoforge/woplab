from pathlib import Path

from dynaconf import Dynaconf, Validator
from platformdirs import PlatformDirs


dirs = PlatformDirs("woplab", "texnoforge", roaming=True)

CONFIG_FILE = 'woplab.toml'

USER_DATA_PATH = dirs.user_data_path
USER_CONFIG_PATH = dirs.user_config_path / CONFIG_FILE
SITE_CONFIG_PATH = dirs.site_config_path / CONFIG_FILE

SETTINGS_FILES = [Path(CONFIG_FILE), USER_CONFIG_PATH, SITE_CONFIG_PATH]


cfg = Dynaconf(
    envvar_prefix='woplab',
    settings_files=SETTINGS_FILES,
)

cfg.validators.register(
    Validator("test_setting", default='test'),
)

cfg.validators.validate()
