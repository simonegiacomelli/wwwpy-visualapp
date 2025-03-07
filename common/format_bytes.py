def format_bytes(size: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]
    factor = 1024
    for unit in units:
        if size < factor:
            return f"{size:.1f} {unit}"
        size /= factor
    return f"{size:.1f}{units[-1]}"
