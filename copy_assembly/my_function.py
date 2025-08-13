from pathlib import Path


def strip_path(path: str) -> str:
    """
    Убирает пробелы перед и после слэшами
    """
    return str(Path(*[s.strip() for s in Path(path).parts]))