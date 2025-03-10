from pathlib import Path

import pandas as pd

data_dir = Path(__file__).parent.parent / 'data'
print(data_dir)
csv_dir = data_dir / 'csv'
csv_cache_dir = data_dir / 'csv_cache'


def write_csv_chunks(file_path, chunk_size=50):
    file_path = Path(file_path)
    cache_path = csv_cache_dir / file_path.name
    if cache_path.exists():
        print(f'{file_path} already cached')
        return
    cache_path.mkdir(exist_ok=True)

    chunk_count = 0
    for chunk in pd.read_csv(file_path, chunksize=chunk_size):
        chunk.to_parquet(cache_path / f'chunk_{chunk_count}.parquet')
        chunk_count += 1
        print('.', end='', flush=True)
        if chunk_count % 50 == 0:
            print('', flush=True)


def main():
    for file_path in csv_dir.glob('*.csv'):
        print(file_path)
        write_csv_chunks(file_path)


if __name__ == '__main__':
    main()
