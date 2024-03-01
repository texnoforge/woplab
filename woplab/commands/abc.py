from pathlib import Path

import click

from texnomagic import cli_common as txm_cli_common

from woplab.console import console
from woplab import svg



@click.group()
def abc():
    """
    Interact with TexnoMagic alphabets.
    """


@abc.command()
@click.argument('abc', required=False)
@click.option('-O', '--result-dir', type=Path,
              help=("Save results into specified dir."
                    "  [default: ./$ABC_DIR/]"))
def export_images(abc, result_dir=None):
    """
    Export symbol images of selected TexnoMagic alphabet.
    """
    format = 'png'

    abc = txm_cli_common.get_alphabet_of_fail(abc)
    abc.load()

    if not result_dir:
        result_dir = Path(abc.path.name)

    result_dir.mkdir(parents=True, exist_ok=True)
    for s in abc.symbols:
        in_path = s.get_image_path()
        out_path = result_dir / f'{s.meaning}.{format}'
        console.print(
            f"[bold_white]CONVERT[/]: [[blue]SVG[/]] {in_path} -> "
            f"[[green]{format.upper()}[/]] {out_path}"
        )
        svg.svg2png(in_path, out_path)
    print(result_dir)


WOPLAB_CLI_COMMANDS = [abc]
