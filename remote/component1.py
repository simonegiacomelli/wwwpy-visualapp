from __future__ import annotations
import io
import logging
import time

import js
import wwwpy.remote.component as wpc
from wwwpy.remote import micropip_install
from wwwpy.remote.jslib import script_load_once
import pandas as pd

from remote.time_series_component import TimeSeriesComponent  # noqa
from server import rpc

logger = logging.getLogger(__name__)


class Component1(wpc.Component, tag_name='component-1'):
    _select_csv: js.HTMLSelectElement = wpc.element()
    btn_prev: js.HTMLButtonElement = wpc.element()
    _inp_chunk: js.HTMLInputElement = wpc.element()
    btn_next: js.HTMLButtonElement = wpc.element()
    pre1: js.HTMLPreElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
<div>component-1</div>
<style> * { margin: 0.25em }</style>

<select data-name="_select_csv">
            <option value="option1">Option 1</option>
            <option value="option2">Option 2</option>
            <option value="option3">Option 3</option>
        </select>
<br>
<button data-name="btn_prev"><- prev</button>
<input data-name="_inp_chunk" placeholder="input1" style="width: 4em" type="text" readonly>
<button data-name="btn_next">next -></button>
<br>
<br>
<time-series-plot></time-series-plot>
<pre data-name="pre1"></pre>
"""
        self._inp_chunk.value = '0'

    async def after_init_component(self):
        await self._load_csv_options()
        logger.info('pandas and fastparquet installed')

    async def _load_csv_options(self):
        self._select_csv.innerHTML = ''
        self.csv_list = await rpc.csv_list()
        self._add_option('-1', 'Select CSV...')
        for i, csv_info in enumerate(self.csv_list):
            value = f'{i}'
            text = f'{csv_info.name} ({csv_info.chunk_number} chunks / {csv_info.file_size_human()} total)'
            self._add_option(value, text)

    async def _load_chunk(self, chunk_delta: int = 0):
        self.pre1.textContent = 'loading...'
        try:

            csv_info = self._get_current_csv_info()
            if chunk_delta != 0:
                self._chunk_index_add(chunk_delta, csv_info.chunk_number)
            logger.debug(f'csv_info: {csv_info}')
            chunk_index = int(self._inp_chunk.value)
            start_time = time.perf_counter_ns()
            df_bytes = await rpc.csv_get_chunk(csv_info.name, chunk_index)
            end_time = time.perf_counter_ns()
            load_timings = f'load_chunk: {(end_time - start_time) / 1_000_000:.2f} milliseconds'

            df = pd.read_parquet(io.BytesIO(df_bytes))
            logger.debug(f'df: {type(df)}')
            logger.debug(f'df: {df.head()}')
            #         print some statics of the dataframe
            logger.debug(f'df.describe(): {df.describe()}')
            record_count = f'record_count: {len(df)}'
            self.pre1.textContent = f'{load_timings}\n\n{record_count}\n\n{df.head()}\n\n{df.describe()}'
        except Exception as e:
            self.pre1.textContent = f'Error: {e}'

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

    async def btn_prev__click(self, event):
        await self._load_chunk(-1)

    async def btn_next__click(self, event):
        await self._load_chunk(1)

    def _chunk_index_add(self, delta, max_chunk):
        i = int(self._inp_chunk.value) + delta
        if i < 0:
            i = 0
        if i >= max_chunk:
            i = max_chunk - 1

        self._inp_chunk.value = str(i)

    async def _select_csv__change(self, event):
        await self._load_chunk()
