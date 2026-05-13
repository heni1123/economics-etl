import asyncio
import logging
import time
from typing import Callable, Any, Optional

class ErrorHandler:
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger

    async def retry_with_backoff(self, func: Callable[..., Any], *args: Any, max_retries: int = 3, backoff_factor: int = 1, **kwargs: Any) -> Optional[Any]:
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                wait_time = backoff_factor * (2 ** attempt)
                self.logger.error(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {wait_time} seconds.")
                await asyncio.sleep(wait_time)
        self.logger.error(f"All {max_retries} attempts failed for function {func.__name__}.")
        return None

    def log_audit_trail(self, rows_extracted: int, rows_loaded: int, status: str, error_message: Optional[str] = None) -> None:
        self.logger.info(f"Audit Trail - Rows Extracted: {rows_extracted}, Rows Loaded: {rows_loaded}, Status: {status}, Error Message: {error_message if error_message else 'None'}")

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ETL_ErrorHandler")
    error_handler = ErrorHandler(logger)

    async def sample_api_call() -> str:
        # Simulate API call
        raise Exception("Simulated API failure")

    async def main() -> None:
        result = await error_handler.retry_with_backoff(sample_api_call)
        if result is None:
            error_handler.log_audit_trail(0, 0, "failed", "API call failed after retries")
        else:
            error_handler.log_audit_trail(1, 1, "success")

    asyncio.run(main())