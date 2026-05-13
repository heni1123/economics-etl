import asyncio
import logging
import time
from typing import Callable, Any

class ErrorHandler:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    async def retry_with_backoff(self, func: Callable[..., Any], *args: Any, max_retries: int = 3, backoff_factor: int = 1, **kwargs: Any) -> Any:
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                wait_time = backoff_factor * (2 ** attempt)
                self.logger.error(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {wait_time} seconds.")
                await asyncio.sleep(wait_time)
        self.logger.error(f"All {max_retries} attempts failed for function {func.__name__}.")
        raise Exception(f"Function {func.__name__} failed after {max_retries} attempts.")

    def log_audit(self, rows_extracted: int, rows_loaded: int, status: str, error_message: str = '') -> None:
        self.logger.info(f"Audit Log - Rows Extracted: {rows_extracted}, Rows Loaded: {rows_loaded}, Status: {status}, Error Message: {error_message}")

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ETL_Error_Handler")
    error_handler = ErrorHandler(logger)

    async def sample_api_call():
        # Simulate API call
        raise Exception("Simulated API failure")

    async def main():
        try:
            await error_handler.retry_with_backoff(sample_api_call)
        except Exception as e:
            error_handler.log_audit(0, 0, "failed", str(e))

    asyncio.run(main())