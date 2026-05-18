import asyncio
import logging
import time
from typing import Callable, Any

class ErrorHandler:
    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.logger = self.setup_logging()

    def setup_logging(self) -> logging.Logger:
        logger = logging.getLogger("ETL_Error_Handler")
        logger.setLevel(logging.INFO)
        handler = logging.FileHandler("etl_error_handler.log")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    async def execute_with_retry(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        for attempt in range(self.max_retries):
            try:
                result = await func(*args, **kwargs)
                self.logger.info(f"Function {func.__name__} executed successfully.")
                return result
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}")
                if attempt < self.max_retries - 1:
                    wait_time = self.backoff_factor * (2 ** attempt)
                    self.logger.info(f"Retrying in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.critical(f"All attempts failed for {func.__name__}. Raising exception.")
                    raise

    def log_audit_trail(self, message: str) -> None:
        self.logger.info(f"AUDIT: {message}")

error_handler = ErrorHandler()