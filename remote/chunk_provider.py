from __future__ import annotations

import io

import pandas as pd

from common.csv_info import CsvInfo
from server import rpc


class ChunkProvider:

    def __init__(self, csv_info: CsvInfo):
        self.csv_info = csv_info

    async def get_chunk(self, chunk_index: int) -> pd.DataFrame:
        df_bytes = await rpc.csv_get_chunk(self.csv_info.name, chunk_index)
        df = pd.read_parquet(io.BytesIO(df_bytes))
        return df
