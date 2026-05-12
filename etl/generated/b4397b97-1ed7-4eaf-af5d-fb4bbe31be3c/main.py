import argparse
import asyncio
import logging
import signal
import time
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ETLPipeline:
    def __init__(self, config: str, dry_run: bool, phase: str):
        self.config = config
        self.dry_run = dry_run
        self.phase = phase
        self.execution_summary: Dict[str, int] = {
            "rows_extracted": 0,
            "rows_loaded": 0,
            "duration": 0
        }

    async def run(self):
        start_time = time.time()
        logger.info("Starting ETL pipeline...")
        # Simulate ETL phases
        await self.extract()
        await self.transform()
        await self.load()
        self.execution_summary["duration"] = time.time() - start_time
        logger.info(f"ETL pipeline completed in {self.execution_summary['duration']} seconds.")
        logger.info(f"Rows extracted: {self.execution_summary['rows_extracted']}, Rows loaded: {self.execution_summary['rows_loaded']}")

    async def extract(self):
        # Simulate data extraction
        logger.info("Extracting data...")
        await asyncio.sleep(1)  # Simulate delay
        self.execution_summary["rows_extracted"] = 100  # Simulated row count

    async def transform(self):
        # Simulate data transformation
        logger.info("Transforming data...")
        await asyncio.sleep(1)  # Simulate delay

    async def load(self):
        # Simulate data loading
        logger.info("Loading data...")
        await asyncio.sleep(1)  # Simulate delay
        self.execution_summary["rows_loaded"] = 100  # Simulated row count

async def main():
    parser = argparse.ArgumentParser(description="ETL Pipeline for Global Economic Indicators")
    parser.add_argument("--config", required=True, help="Path to the configuration file")
    parser.add_argument("--dry-run", action="store_true", help="Run the pipeline in dry run mode")
    parser.add_argument("--phase", required=True, help="Specify the phase to run")
    args = parser.parse_args()

    pipeline = ETLPipeline(config=args.config, dry_run=args.dry_run, phase=args.phase)

    await pipeline.run()

def signal_handler(sig, frame):
    logger.info("Graceful shutdown initiated.")
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"ETL pipeline failed with error: {e}")
        exit(2)