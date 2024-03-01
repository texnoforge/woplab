"""
woplab CLI
"""
import logging
import os
import pkgutil

import click

from woplab import __version__
from woplab import commands
from woplab.config import cfg


log = logging.getLogger(__name__)


CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help'],
}


def required_option(option):
    val = cfg.get(option)
    if val:
        return val
    raise click.ClickException("Missing required config option: %s" % option)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('-c', '--config', type=click.Path(exists=True, dir_okay=False),
              help='Use specified woplab config file.')
@click.version_option(__version__, message='%(version)s',
                      help="Show woplab version and exit.")
def cli(config):
    """
    Words of Power Laboratory
    """
    if config:
        cfg.load_file(path=config)


def __load_commands():
    """
    load available woplab commands

    should only be called once on module load
    """
    pkgpath = os.path.dirname(commands.__file__)
    for _, modname, _ in pkgutil.iter_modules([pkgpath]):
        modpath = "woplab.commands.%s" % (modname)
        mod = __import__(modpath, fromlist=[''])
        cmds = getattr(mod, 'WOPLAB_CLI_COMMANDS', None)
        if not cmds:
            log.warning('command module with no CLI commands: %s', modpath)
            continue
        for cmd in cmds:
            cli.add_command(cmd)


__load_commands()


def main():
    cli()


if __name__ == '__main__':
    main()
