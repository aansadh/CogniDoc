import time, logging
from contextlib import asynccontextmanager
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)

@asynccontextmanager
async def timing_block(name: str):
    start_time = time.monotonic()
    try:
        yield 
    finally:
        end_time = time.monotonic()
        duration = end_time - start_time
        logger.info(f"Operation '{name}' executed in {duration:.4f} seconds.")


def log_duration(func):
    @wraps(func) 
    async def async_wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = await func(*args, **kwargs) 
        elapsed_time = (time.monotonic() - start_time) 
        logger.info(f"Function '{func.__name__}' executed in {elapsed_time:.2f} ms")
        return result

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.monotonic()
        result = func(*args, **kwargs) 
        elapsed_time = (time.monotonic() - start_time)
        logger.info(f"Function '{func.__name__}' executed in {elapsed_time:.2f} ms")
        return result

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper