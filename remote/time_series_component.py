import math
import js
import wwwpy.remote.component as wpc
from wwwpy.remote import dict_to_js
from wwwpy.remote.jslib import script_load_once


class TimeSeriesComponent(wpc.Component, tag_name="time-series-plot"):
    btn_left: js.HTMLButtonElement = wpc.element()
    btn_right: js.HTMLButtonElement = wpc.element()
    plotDiv: js.HTMLDivElement = wpc.element()

    def init_component(self):
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
        self.windowSize = 100
        self.shift_points = 10
        self.xData = [i for i in range(self.windowSize)]
        self.yData = [math.sin(i * 0.1) for i in range(self.windowSize)]

    async def after_init_component(self):
        await script_load_once("https://cdn.plot.ly/plotly-3.0.0.min.js", charset="utf-8")
        layout = {
            "xaxis": {"range": [self.xData[0], self.xData[-1]]},
            "yaxis": {"title": "Amplitude"},
            "title": "Dynamic Time Series Shift",
        }
        inp = [{"x": self.xData, "y": self.yData, "mode": "lines", "name": "Sinusoid"}]

        js.Plotly.newPlot(self.plotDiv, dict_to_js(inp), dict_to_js(layout))

    async def btn_right__click(self, event):
        new_xs = list(range(self.xData[-1] + 1, self.xData[-1] + self.shift_points + 1))
        new_ys = [math.sin(x * 0.1) for x in new_xs]

        self.xData = self.xData[self.shift_points:] + new_xs
        self.yData = self.yData[self.shift_points:] + new_ys

        layout_update = {"xaxis": {"range": [self.xData[0], self.xData[-1]]}}
        await self._update(layout_update)

    async def btn_left__click(self, event):
        new_xs = list(range(self.xData[0] - self.shift_points, self.xData[0]))
        new_ys = [math.sin(x * 0.1) for x in new_xs]

        self.xData = new_xs + self.xData[:-self.shift_points]
        self.yData = new_ys + self.yData[:-self.shift_points]

        layout_update = {"xaxis": {"range": [self.xData[0], self.xData[-1]]}}
        await self._update(layout_update)

    async def _update(self, layout_update):
        data = {"x": [self.xData], "y": [self.yData]}
        js.Plotly.update(self.plotDiv, dict_to_js(data), dict_to_js(layout_update))
