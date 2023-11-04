
from .config import DEBUG_LOG, LOG_LEVEL

def log(*args):
    if DEBUG_LOG:
        print(*args)

def log1(*args):
    if DEBUG_LOG and LOG_LEVEL >= 1:
        print(*args)