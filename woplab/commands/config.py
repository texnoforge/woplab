import click
import toml

from woplab import config as config_mod
from woplab.config import cfg


@click.command()
def config():
    """
    Show woplab config.
    """
    print("woplab config files:")
    for settings_file in config_mod.SETTINGS_FILES:
        if settings_file.exists():
            state = "exists"
        else:
            state = "doesn't exist"
        print(f"- {settings_file} {state}")

    print("\nEFFECTIVE CONFIG:\n")
    print(toml.dumps(cfg.as_dict()))


WOPLAB_CLI_COMMANDS = [config]
