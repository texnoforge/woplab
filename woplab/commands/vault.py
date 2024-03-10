from collections import defaultdict
from pathlib import Path
import webbrowser

import click

from texnomagic.abcs import TexnoMagicAlphabets
from texnomagic.drawing import TexnoMagicDrawing

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


@vault.command()
@click.option('-a', '--abc', multiple=True,
              help="TexnoMagic alphabet(s) to export.")
@click.option('-s', '--symbol', multiple=True,
              help="TexnoMagic symbol(s) to export.")
@click.option('-t', '--drawings-tag', multiple=True,
              help="Drawings tag(s) to export.")
@click.option('-m', '--min-score', type=float, default=0.65, show_default=True,
              help="Only show results above this score.")
@click.option('-M', '--max-score', type=float, default=float('inf'),
              help="Only show results below this score.")
@click.option('--norm/--no-norm', default=True, show_default=True,
              help='Normalize drawing during export.')
@click.option('-d', '--dry-run', is_flag=True,
              help="Dry run - don't really export anything.")
@click.option('-n', '--only-new', is_flag=True,
              help="Only print new exports.")
@click.option('--overwrite', is_flag=True,
              help="[!] Overwrite existing drawings.")
def export(abc, symbol, drawings_tag, min_score, max_score, norm, dry_run, only_new, overwrite):
    """
    Export drawings from the Vault
    into respective TexnoMagic alphabets.
    """
    abc_tag = 'user'
    vd = vault_mod.VaultDrawings()
    abcs = TexnoMagicAlphabets()

    stats = defaultdict(lambda: defaultdict(int))

    for abc_handle, abc_tree in vd.tree.items():
        if abc and abc_handle not in abc:
            continue
        abc_id = f"{abc_tag}:{abc_handle}"
        abc_dst = abcs.get_alphabet(abc_id)
        if not abc_dst:
            console.print(f"[red]ERROR: destination alphabet not found: {abc_id}[/]")
            return
        console.print(abc_dst.pretty())
        for symbol_handle, symbol_tree in abc_tree.items():
            if symbol and symbol_handle not in symbol:
                continue
            symbol_dst = abc_dst.get_symbol(symbol_handle)
            if not symbol_dst:
                console.print(f"[red]ERROR: destination symbol not found: {symbol_handle}[/]")
                return
            console.print(symbol_dst.pretty())
            for tag, drawings_paths in symbol_tree.items():
                if drawings_tag and tag not in drawings_tag:
                    continue
                console.print(f"  [magenta]{tag.upper()}[/] tag:")
                scores = []
                for drawing_path in drawings_paths:
                    drawing = TexnoMagicDrawing(drawing_path)
                    if norm:
                        drawing.normalize()
                    score = symbol_dst.model.score(drawing)
                    scores.append((drawing, score))

                scores.sort(key=lambda s: s[1], reverse=True)
                for drawing, score in scores:
                    drawing.path = symbol_dst.drawings_path / drawing.name
                    do_export = False
                    is_new = False
                    if score < min_score or score > max_score:
                        action_str = "[red]BAD SCORE[/]"
                        stats['bad_score'][tag] += 1
                    elif drawing.path.exists():
                        if overwrite:
                            do_export = True
                            action_str = "[green]OVERWRITE[/]"
                            stats['overwrite'][tag] += 1
                        else:
                            action_str = "[green]EXISTS[/]"
                            stats['exists'][tag] += 1
                        stats['present'][tag] += 1
                    else:
                        do_export = True
                        is_new = True
                        action_str = "[bright_green]NEW[/]"
                        stats['new'][tag] += 1
                        stats['present'][tag] += 1

                    stats['total'][tag] += 1

                    if not only_new or is_new:
                        console.print(f"    {action_str} {drawing.name}: {score.pretty(rating=True)}")

                    if do_export:
                        if dry_run:
                            if not only_new:
                                console.print(
                                    f"      [yellow]DRY RUN[/]: [green]EXPORT[/]: {drawing.name}"
                                    f" [cyan]{abc_dst.name}[/] {symbol_dst.pretty()}"
                                )
                            continue

                        drawing.save()


        def print_stats(stat, text, percent=True):
            st = stats[stat]
            n = sum(st.values())
            if n == 0:
                return
            tags_lines = []
            for tag, color in [('good', 'green'), ('bad', 'red')]:
                tag_text = f"{st[tag]}"
                if percent:
                    p = 0.0
                    t = stats['total'][tag]
                    if t > 0:
                        p = round(100.0 * st[tag] / t)
                    tag_text += f" | [blue]{p} %[/]"
                tag_text += f" [{color}]{tag.upper()}[/]"
                tags_lines.append(tag_text)
            tags_text = ", ".join(tags_lines)
            console.print(f"{n} {text} ({tags_text})")

        print()
        print_stats('new', '[bold][bright_green]NEW[/][/]')
        print_stats('exists', '[green]EXISTING[/]')
        print_stats('overwrite', '[bright_green]OVERWRITTEN[/]')
        print_stats('bad_score', '[red]BAD SCORE[/]')
        print()
        print_stats('present', '[magenta]EXPORTED[/]')


WOPLAB_CLI_COMMANDS = [vault]
