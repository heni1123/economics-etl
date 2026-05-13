import asyncio
import logging
import time
from typing import Callable, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorHandler:
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    async def execute_with_retry(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Optional[Any]:
        for attempt in range(self.max_retries):
            try:
                result = await func(*args, **kwargs)
                logger.info(f"Function {func.__name__} executed successfully.")
                return result
            except Exception as e:
                wait_time = self.backoff_factor ** attempt
                logger.error(f"Error executing {func.__name__}: {e}. Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
        logger.error(f"Function {func.__name__} failed after {self.max_retries} attempts.")
        return None

    def log_audit(self, rows_extracted: int, rows_loaded: int, status: str, error_message: Optional[str] = None) -> None:
        logger.info(f"Audit Log - Rows Extracted: {rows_extracted}, Rows Loaded: {rows_loaded}, Status: {status}, Error: {error_message if error_message else 'None'}")

error_handler = ErrorHandler()