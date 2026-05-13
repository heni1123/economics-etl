import argparse
import asyncio
import logging
import signal
import time
from typing import Any, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ETLPipeline:
    def __init__(self, config: str, dry_run: bool, phase: str):
        self.config = config
        self.dry_run = dry_run
        self.phase = phase
        self.execution_summary: Dict[str, Any] = {
            "total_duration": 0,
            "phases": {}
        }

    async def run(self) -> int:
        start_time = time.time()
        try:
            await self.extract()
            await self.transform()
            await self.load()
            status = 0
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            status = 2
        finally:
            self.execution_summary["total_duration"] = time.time() - start_time
            logger.info(f"Execution Summary: {self.execution_summary}")
        return status

    async def extract(self):
        logger.info("Extracting data...")
        # Extraction logic here
        await asyncio.sleep(1)  # Simulate async operation
        logger.info("Data extraction completed.")

    async def transform(self):
        logger.info("Transforming data...")
        # Transformation logic here
        await asyncio.sleep(1)  # Simulate async operation
        logger.info("Data transformation completed.")

    async def load(self):
        logger.info("Loading data...")
        # Loading logic here
        await asyncio.sleep(1)  # Simulate async operation
        logger.info("Data loading completed.")

async def main() -> None:
    parser = argparse.ArgumentParser(description="Global Economic Indicators ETL Pipeline")
    parser.add_argument("--config", required=True, help="Path to the configuration file")
    parser.add_argument("--dry-run", action="store_true", help="Run the pipeline in dry run mode")
    parser.add_argument("--phase", required=True, help="Specify the phase to run")
    args = parser.parse_args()

    pipeline = ETLPipeline(config=args.config, dry_run=args.dry_run, phase=args.phase)
    exit_code = await pipeline.run()
    exit(exit_code)

def signal_handler(sig: int, frame: Any) -> None:
    logger.info("Graceful shutdown initiated.")
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    asyncio.run(main())