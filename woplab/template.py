from importlib import resources as impresources
import shutil

import jinja2

from woplab import static


template_loader = jinja2.PackageLoader('woplab', 'templates')
static_loader = jinja2.PackageLoader('woplab', 'static')

env = jinja2.Environment(
    loader=template_loader)


def render_template(template, out_path, **kwargs):
    t = env.get_template(template)
    txt = t.render(**kwargs)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(txt)


def copy_static(src, out_path):
    static_path = impresources.files(static) / src
    shutil.copytree(static_path, out_path, dirs_exist_ok=True)
