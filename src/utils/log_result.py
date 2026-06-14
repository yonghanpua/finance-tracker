import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

def get_logger(log_path: str) -> logging.Logger:
    # Build path: logs/yyyy/mm/dd/Log.txt
    now = datetime.now()
    base = Path(log_path)
    dated_path = base.parent / str(now.year) / f"{now.month:02d}" / f"{now.day:02d}" / base.name

    # Create folders if they don't exist
    dated_path.parent.mkdir(parents=True, exist_ok=True)

    log_key = str(dated_path)
    logger = logging.getLogger(log_key)

    if not logger.handlers:
        handler = RotatingFileHandler(dated_path, maxBytes=5_000_000, backupCount=3)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='[%Y-%m-%d %H:%M:%S]'
        ))
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
    return logger

def logResult(output_path: str, result:str):
    get_logger(output_path).info(result)
    
    