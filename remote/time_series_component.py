import js
import wwwpy.remote.component as wpc
from wwwpy.remote import dict_to_js
from wwwpy.remote.jslib import script_load_once
import asyncio

from remote.chunk_provider import ChunkProvider


class TimeSeriesComponent(wpc.Component, tag_name="time-series-plot"):
    btn_left: js.HTMLButtonElement = wpc.element()
    btn_right: js.HTMLButtonElement = wpc.element()
    plotDiv: js.HTMLDivElement = wpc.element()

    def init_component(self):
        # language=html
        self.element.innerHTML = """
        <div>
            <button data-name="btn_left">&larr; Left</button>
            <button data-name="btn_right">Right &rarr;</button>
        </div>
        <div data-name="plotDiv" style="width:80%; height:400px; margin:auto;"></div>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin: 20px; }
            button { margin: 10px; padding: 10px 20px; font-size: 16px; cursor: pointer; }
        </style>
        """
        self.loaded_chunks = []
        self.current_chunk_index = 0
        self.window_size = 16
        self._chunk_provider: ChunkProvider = None

    async def after_init_component(self):
        await script_load_once("https://cdn.plot.ly/plotly-3.0.0.min.js", charset="utf-8")

    @property
    def chunk_provider(self):
        return self._chunk_provider

    @chunk_provider.setter
    def chunk_provider(self, provider: ChunkProvider):
        self._chunk_provider = provider
        asyncio.create_task(self._load_initial_chunks())

    async def _load_initial_chunks(self):
        for i in range(self.window_size):
            if i < self._chunk_provider.csv_info.chunk_number:
                chunk = await self._chunk_provider.get_chunk(i)
                self.loaded_chunks.append(chunk)
        xData, yData = self._concatenate_chunks()
        layout = {"xaxis": {"range": [xData[0], xData[-1]]}, "yaxis": {"title": "Amplitude"},
                  "title": "Time Series Data"}
        trace = [{"x": xData, "y": yData, "mode": "lines", "name": "Chunk Data"}]
        js.Plotly.newPlot(self.plotDiv, dict_to_js(trace), dict_to_js(layout))

    def _concatenate_chunks(self):
        import pandas as pd
        combined = pd.concat(self.loaded_chunks)
        return combined["Sample Time"].tolist(), combined["ivECG_filtered"].tolist()

    async def _update_plot(self):
        xData, yData = self._concatenate_chunks()
        layout_update = {"xaxis": {"range": [xData[0], xData[-1]]}}
        data_update = {"x": [xData], "y": [yData]}
        js.Plotly.update(self.plotDiv, dict_to_js(data_update), dict_to_js(layout_update))

    async def btn_right__click(self, event):
        total = self._chunk_provider.csv_info.chunk_number
        if self.current_chunk_index + self.window_size < total:
            next_index = self.current_chunk_index + self.window_size
            new_chunk = await self._chunk_provider.get_chunk(next_index)
            self.loaded_chunks.pop(0)
            self.loaded_chunks.append(new_chunk)
            self.current_chunk_index += 1
            await self._update_plot()

    async def btn_left__click(self, event):
        if self.current_chunk_index > 0:
            prev_index = self.current_chunk_index - 1
            new_chunk = await self._chunk_provider.get_chunk(prev_index)
            self.loaded_chunks.pop(-1)
            self.loaded_chunks.insert(0, new_chunk)
            self.current_chunk_index -= 1
            await self._update_plot()
