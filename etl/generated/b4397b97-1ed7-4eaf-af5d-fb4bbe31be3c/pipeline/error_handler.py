import asyncio
import logging
import time
from typing import Callable, Any, Optional

class ErrorHandler:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    async def retry_with_backoff(self, func: Callable[..., Any], *args: Any, max_retries: int = 3, **kwargs: Any) -> Any:
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                wait_time = 2 ** attempt
                self.logger.error(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {wait_time} seconds.")
                await asyncio.sleep(wait_time)
        self.logger.critical(f"All {max_retries} attempts failed for function {func.__name__}.")
        raise Exception(f"Function {func.__name__} failed after {max_retries} attempts.")

    def log_audit(self, rows_extracted: int, rows_loaded: int, status: str, error_message: Optional[str] = None) -> None:
        self.logger.info(f"Audit Log - Rows Extracted: {rows_extracted}, Rows Loaded: {rows_loaded}, Status: {status}, Error: {error_message or 'None'}")

    def log_completion(self, task_id: str, message: str) -> None:
        self.logger.info(f"Task {task_id} completed: {message}")

    def log_error(self, task_id: str, error_message: str) -> None:
        self.logger.error(f"Task {task_id} encountered an error: {error_message}")