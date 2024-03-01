import subprocess


def svg2png(svg_path, png_path, width=1000):
    """
    Convert SVG to PNG using Inkscape.
    """
    cmd = [
        'inkscape',
        '--export-background-opacity=0',
#       f'--export-width={width}',
        '-o', str(png_path),
        str(svg_path)
    ]
    r = subprocess.run(cmd)
    print(r)
