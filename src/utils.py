# utility functions

import logging
import re
import json
from pathlib import Path

def setup_logger(name: str) -> logging.Logger:
    """Configure and return a logger with file and console handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    file_handler = logging.FileHandler(log_dir / f'{name}.log')
    file_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(logging.StreamHandler())
    
    return logger


def extract_json_from_markdown(text: str) -> str:
    # If the response is a fenced code block, remove the fence including optional `json` hint.[1][2][3]
    fenced_pattern = r"^```(?:json)?\s*(.*?)\s*```"
    m = re.search(fenced_pattern, text.strip(), flags=re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return text.strip()