import argparse
import asyncio
import logging
import signal
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ETLPipeline:
    def __init__(self, config: str, dry_run: bool, phase: str):
        self.config = config
        self.dry_run = dry_run
        self.phase = phase
        self.execution_summary = {
            "total_rows_extracted": 0,
            "total_rows_loaded": 0,
            "phase_durations": {}
        }

    async def extract(self):
        start_time = time.time()
        # Simulate extraction logic
        await asyncio.sleep(1)
        self.execution_summary["total_rows_extracted"] = 1000
        duration = time.time() - start_time
        self.execution_summary["phase_durations"]["extract"] = duration
        logger.info(f"Extract phase completed in {duration:.2f} seconds.")

    async def transform(self):
        start_time = time.time()
        # Simulate transformation logic
        await asyncio.sleep(1)
        duration = time.time() - start_time
        self.execution_summary["phase_durations"]["transform"] = duration
        logger.info(f"Transform phase completed in {duration:.2f} seconds.")

    async def load(self):
        start_time = time.time()
        # Simulate loading logic
        await asyncio.sleep(1)
        self.execution_summary["total_rows_loaded"] = 1000
        duration = time.time() - start_time
        self.execution_summary["phase_durations"]["load"] = duration
        logger.info(f"Load phase completed in {duration:.2f} seconds.")

    async def run(self):
        await self.extract()
        await self.transform()
        await self.load()

    def summary(self):
        logger.info("Execution Summary:")
        logger.info(f"Total Rows Extracted: {self.execution_summary['total_rows_extracted']}")
        logger.info(f"Total Rows Loaded: {self.execution_summary['total_rows_loaded']}")
        for phase, duration in self.execution_summary["phase_durations"].items():
            logger.info(f"{phase.capitalize()} Duration: {duration:.2f} seconds")

async def main(config: str, dry_run: bool, phase: str) -> int:
    pipeline = ETLPipeline(config, dry_run, phase)
    try:
        await pipeline.run()
        pipeline.summary()
        return 0
    except Exception as e:
        logger.error(f"ETL process failed: {e}")
        return 2

def signal_handler(sig, frame):
    logger.info("Graceful shutdown initiated.")
    exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Global Economic Indicators ETL Pipeline")
    parser.add_argument("--config", type=str, required=True, help="Path to the configuration file")
    parser.add_argument("--dry-run", action="store_true", help="Run the pipeline in dry run mode")
    parser.add_argument("--phase", type=str, choices=["extract", "transform", "load"], required=True, help="Specify the phase to run")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    exit_code = asyncio.run(main(args.config, args.dry_run, args.phase))
    exit(exit_code)