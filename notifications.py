from logging import getLogger

logger = getLogger(__name__)

try:
    from win11toast import notify
except ModuleNotFoundError:
    logger.warning('Module not found')

def notify_win(msg, title=None, url=None):
    try:
        if title:
            notify(title, msg, on_click=url)
        else:
            notify(msg, on_click=url)
    except ModuleNotFoundError:
        None