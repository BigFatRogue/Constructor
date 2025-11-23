from datetime import datetime


def get_now_time() -> str:
    now = datetime.now()
    return f'{now.day:02}.{now.month:02}.{now.year}_{now.hour:02}:{now.minute:02}:{now.second:02}'