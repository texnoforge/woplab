from collections import defaultdict
from datetime import datetime
from typing import Any
import os.path
from pathlib import Path

import pandas as pd

from woplab.template import render_template, copy_static


pd.options.plotting.backend = "plotly"


class MissingModule():
    def __init__(self, mod) -> None:
        self.__mod = mod

    def __getattribute__(self, __name: str) -> Any:
        if __name[0] == '_' or __name == 'name':
            return super().__getattribute__(__name)
        msg = f"This operation requires optional module: {self.__mod}"
        raise ModuleNotFoundError(msg)


WOPVAULT = False
try:
    from wopvault import config  # noqa
    WOPVAULT = True
except ModuleNotFoundError:
    config = MissingModule('wopvault')


def tag_from_dir(drawings_dir):
    _, _, tag = drawings_dir.partition('_')
    return tag or 'good'


class VaultStats:
    def __init__(self, path=None):
        self.path = Path(path or config.cfg.vault_path)
        self.compute_stats()

    def compute_stats(self):
        self.n_tags = defaultdict(int)
        self.n_symbols = defaultdict(int)
        self.n_symbols_tags = defaultdict(lambda: defaultdict(int))
        self.times = defaultdict(str)

        for p in self.path.glob('alphabets/*/symbols/*/drawings*/*.csv'):
            drawings_dir = p.parts[-2]
            tag = tag_from_dir(drawings_dir)
            symbol = p.parts[-3]
            _abc = p.parts[-5]
            mtime = os.path.getmtime(p)
            dt = datetime.fromtimestamp(mtime)

            self.n_tags[tag] += 1
            self.n_symbols[symbol] += 1
            self.n_symbols_tags[symbol][tag] += 1
            self.times[dt] = tag

        self.n_drawings = len(self.times)
        self.times = dict(sorted(self.times.items()))

    def get_symbols_badness(self, percent=False, sort=True, reverse=False):
        badness = defaultdict(float)
        for symbol, tags in self.n_symbols_tags.items():
            n_good = tags['good']
            n_bad = tags['bad']
            r = 0.0
            if n_good == 0:
                if n_bad > 0:
                    r = 1.0
            else:
                r = n_bad / float(n_good)
            if percent:
                r = round(100.0 * r)
            badness[symbol] = r
        if sort:
            badness = dict(sorted(badness.items(), key=lambda item: item[1], reverse=reverse))
        return badness

    def get_symbols_tags_plot_data(self):
        symbols = []
        n = {
            'good': [],
            'bad': [],
        }
        # sort symbols by number of 'good' tags
        for symbol, tags in sorted(self.n_symbols_tags.items(),
                                key=lambda s: s[1]['good']):
            symbols.append(symbol)
            n['good'].append(tags['good'])
            n['bad'].append(tags['bad'])

        df = pd.DataFrame(n, index=symbols)
        df.index.name = 'symbol'
        df.columns.name = 'drawing'
        return df

    def get_symbols_badness_plot_data(self):
        badness = self.get_symbols_badness(percent=True)
        df = pd.DataFrame({'badness': badness.values()}, index=badness.keys())
        df.index.name = 'symbol'
        return df

    def get_times_plot_data(self):
        dts = []
        data = {
            'good': [],
            'bad': [],
        }
        for dt, tag in self.times.items():
            dts.append(dt)
            data['good'].append(1 if tag != 'bad' else 0)
            data['bad'].append(1 if tag == 'bad' else 0)
        df = pd.DataFrame(data, index=dts)
        df.index.name = 'time'
        df.columns.name = 'drawing'
        # aggregate by hour (for now)
        df_sum = df.groupby(df.index.floor('h')).sum()
        return df_sum


def render_report(path):
    path.mkdir(parents=True, exist_ok=True)
    index_path = path / "index.html"
    vs = VaultStats()
    symbols_tags_data = vs.get_symbols_tags_plot_data()
    symbols_tags_fig = symbols_tags_data.plot.barh(
        text_auto=True,
        title="amout of drawings per symbol",
        labels=dict(value="# drawings"),
        template="plotly_dark",
        height=1000,
    )
    symbols_badness_data = vs.get_symbols_badness_plot_data()
    symbols_badness_fig = symbols_badness_data.plot.barh(
        text_auto=True,
        title="drawing badness (bad / good ratio) per symbol",
        labels=dict(value='badness [%]'),
        template="plotly_dark",
        height=1000,
    )
    times_data = vs.get_times_plot_data()
    times_fig = times_data.plot.bar(
        text_auto=True,
        title="drawings submission through time",
        labels=dict(value="# drawings"),
        template="plotly_dark",
    )
    print(times_data)

    html_args = dict(full_html=False, include_plotlyjs=False)
    render_template("vault/report.html", index_path,
                    symbols_tags_fig=symbols_tags_fig.to_html(**html_args),
                    symbols_badness_fig=symbols_badness_fig.to_html(**html_args),
                    times_fig=times_fig.to_html(**html_args),
                    )
    copy_static("css", path / "css")

    return index_path
