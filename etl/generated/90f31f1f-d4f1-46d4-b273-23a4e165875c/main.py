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
            "start_time": None,
            "end_time": None,
            "durations": {},
            "row_counts": {}
        }

    async def run(self) -> int:
        self.execution_summary["start_time"] = time.time()
        try:
            await self.extract()
            await self.transform()
            await self.load()
            self.execution_summary["end_time"] = time.time()
            self.log_summary()
            return 0
        except Exception as e:
            logger.error(f"ETL pipeline failed: {e}")
            return 2

    async def extract(self):
        logger.info("Starting extraction phase...")
        # Simulate extraction logic
        await asyncio.sleep(1)
        self.execution_summary["row_counts"]["extracted"] = 1000
        logger.info("Extraction phase completed.")

    async def transform(self):
        logger.info("Starting transformation phase...")
        # Simulate transformation logic
        await asyncio.sleep(1)
        self.execution_summary["row_counts"]["transformed"] = 1000
        logger.info("Transformation phase completed.")

    async def load(self):
        logger.info("Starting loading phase...")
        # Simulate loading logic
        await asyncio.sleep(1)
        self.execution_summary["row_counts"]["loaded"] = 1000
        logger.info("Loading phase completed.")

    def log_summary(self):
        logger.info("ETL Execution Summary:")
        logger.info(f"Start Time: {self.execution_summary['start_time']}")
        logger.info(f"End Time: {self.execution_summary['end_time']}")
        logger.info(f"Row Counts: {self.execution_summary['row_counts']}")

async def main() -> None:
    parser = argparse.ArgumentParser(description="Global Economic Indicators ETL")
    parser.add_argument("--config", required=True, help="Path to the configuration file")
    parser.add_argument("--dry-run", action="store_true", help="Run the ETL pipeline in dry run mode")
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