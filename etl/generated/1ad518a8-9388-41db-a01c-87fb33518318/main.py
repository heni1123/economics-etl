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
            "start_time": time.time(),
            "end_time": None,
            "status": "success",
            "error_message": None
        }

    async def extract(self):
        # Simulate extraction logic
        logger.info("Extracting data...")
        await asyncio.sleep(1)
        self.execution_summary["total_rows_extracted"] = 1000

    async def transform(self):
        # Simulate transformation logic
        logger.info("Transforming data...")
        await asyncio.sleep(1)

    async def load(self):
        # Simulate loading logic
        logger.info("Loading data...")
        await asyncio.sleep(1)
        self.execution_summary["total_rows_loaded"] = 1000

    async def run(self):
        await self.extract()
        await self.transform()
        await self.load()

    def log_summary(self):
        self.execution_summary["end_time"] = time.time()
        duration = self.execution_summary["end_time"] - self.execution_summary["start_time"]
        logger.info(f"Execution Summary: {self.execution_summary}")
        logger.info(f"Total Duration: {duration:.2f} seconds")

async def main():
    parser = argparse.ArgumentParser(description="Global Economic Indicators ETL Pipeline")
    parser.add_argument("--config", required=True, help="Path to the configuration file")
    parser.add_argument("--dry-run", action="store_true", help="Run the pipeline in dry run mode")
    parser.add_argument("--phase", required=True, help="Specify the phase of the ETL process")
    args = parser.parse_args()

    pipeline = ETLPipeline(config=args.config, dry_run=args.dry_run, phase=args.phase)

    try:
        await pipeline.run()
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        pipeline.execution_summary["status"] = "failed"
        pipeline.execution_summary["error_message"] = str(e)

    pipeline.log_summary()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    pipeline = None

    def signal_handler(sig, frame):
        logger.info("Graceful shutdown initiated.")
        if pipeline:
            pipeline.execution_summary["status"] = "failed"
        loop.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        loop.run_until_complete(main())
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        exit_code = 2
    else:
        exit_code = 0 if pipeline.execution_summary["status"] == "success" else 1

    loop.close()
    exit(exit_code)