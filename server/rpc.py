import logging

from common.csv_info import CsvInfo
from server import panda_chunk

logger = logging.getLogger(__name__)


async def csv_list() -> list[CsvInfo]:
    res = []
    for f in panda_chunk.csv_cache_dir.glob('*.csv'):
        original_csv = panda_chunk.csv_dir / f.name
        file_size_bytes = original_csv.stat().st_size
        ci = CsvInfo(name=f.name, chunk_number=len(list(f.glob('*.parquet'))), file_size_bytes=file_size_bytes)
        res.append(ci)

    logger.debug(f'csv_list: {res}')
    return res


async def csv_get_chunk(csv_name: str, chunk_index: int) -> bytes:
    chung_file = panda_chunk.csv_cache_dir / csv_name / f'chunk_{chunk_index}.parquet'
    return chung_file.read_bytes()
