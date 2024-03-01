from pathlib import Path
import webbrowser

import click

from woplab import vault as vault_mod
from woplab.console import console


@click.group()
def vault():
    """
    Interact with Words of Power Vault (wopvault) data.

    These commands require 'wopvault' python module to work.
    """


@vault.command()
def stats():
    """
    Show Words of Power Vault statistics.
    """
    vs = vault_mod.VaultStats()

    msg = f"{vs.n_drawings} [bold]total drawings[/]: "
    msg += f"{vs.n_tags['good']} [green]good[/], "
    msg += f"{vs.n_tags['bad']} [red]bad[/]"
    console.print(msg)

    console.print(f"\n{len(vs.n_symbols)} symbols:")
    for symbol, tags in vs.n_symbols_tags.items():
        msg = f"  {vs.n_symbols[symbol]} [bold]{symbol}[/] drawings: "
        msg += f"{tags['good']} [green]good[/], "
        msg += f"{tags['bad']} [red]bad[/]"
        console.print(msg)


@vault.command()
@click.option('-O', '--result-dir', type=Path,
              default=Path('vault-report'), show_default=True,
              help="Save results into specified dir.")
@click.option('-w', '--open-web', is_flag=True,
              help="Open the report in web browser.")
def report(result_dir, open_web=False):
    """
    Generate static HTML report about Vault.
    """
    print(f"rendering vault report: {result_dir}")
    index_path = vault_mod.render_report(result_dir)
    print(f"vault report index: {index_path}")
    if open_web:
        webbrowser.open(index_path)


WOPLAB_CLI_COMMANDS = [vault]
