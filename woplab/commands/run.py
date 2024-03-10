import webbrowser
import click

from woplab.console import console
from woplab.app.main import app, DEFAULT_PORT



@click.command()
@click.option('-p', '--port', type=int,
              default = DEFAULT_PORT, show_default=True,
              help="Run on specified port.")
@click.option('-d', '--debug', is_flag=True,
              help="Debug server.")
def run(port, debug):
    """
    Run the woplab webapp using Flask.
    """
    console.print("[green]RUN[/] Words of Power Laboratory web app using Flask.")
    # open browser first
    url = f'http://localhost:{port}/'
    print(f"Opening web browser: {url}")
    webbrowser.open(url)

    app.run(port=port, debug=debug)


WOPLAB_CLI_COMMANDS = [run]
