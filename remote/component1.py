from __future__ import annotations
import inspect
import io
import logging
import time

import js
import wwwpy.remote.component as wpc
import pandas as pd

from remote.chunk_provider import ChunkProvider
from remote.time_series_component import TimeSeriesComponent  # noqa
from server import rpc

logger = logging.getLogger(__name__)


class Component1(wpc.Component, tag_name='component-1'):
    _select_csv: js.HTMLSelectElement = wpc.element()
    btn_win_plus: js.HTMLButtonElement = wpc.element()
    _inp_chunk: js.HTMLInputElement = wpc.element()
    pre1: js.HTMLPreElement = wpc.element()
    time_series_plot_1: TimeSeriesComponent = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<div>component-1 beta</div>
<style> * { margin: 0.25em }</style>

<select data-name="_select_csv">
            <option value="option1">Option 1</option>
            <option value="option2">Option 2</option>
            <option value="option3">Option 3</option>
        </select>

<time-series-plot data-name='time_series_plot_1'></time-series-plot>
<pre data-name="pre1"></pre>
"""
    async def after_init_component(self):
        self._select_csv.innerHTML = ''
        self.csv_list = await rpc.csv_list()
        self._add_option('-1', 'Select CSV...')
        for i, csv_info in enumerate(self.csv_list):
            value = f'{i}'
            text = f'{csv_info.name} ({csv_info.chunk_number} chunks / {csv_info.file_size_human()} total)'
            self._add_option(value, text)


    def _get_current_csv_info(self):
        csv_index = int(self._select_csv.value)
        if csv_index < 0:
            raise ValueError('Select a CSV file first')
        if csv_index >= len(self.csv_list):
            raise ValueError('Invalid CSV index')

        csv_info = self.csv_list[csv_index]
        return csv_info

    def _add_option(self, value, text):
        option = js.document.createElement('option')
        option.value = value
        option.text = text
        self._select_csv.appendChild(option)

    async def _select_csv__change(self, event):
        csv_info = self._get_current_csv_info()
        self.time_series_plot_1.chunk_provider = ChunkProvider(csv_info)
