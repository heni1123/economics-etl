import argparse
import asyncio
import logging
import signal
import time
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

exit_code = 0

async def run_etl_phase(phase: str) -> Dict[str, int]:
    start_time = time.time()
    logger.info(f"Starting ETL phase: {phase}")
    # Simulate ETL phase processing
    await asyncio.sleep(1)  # Replace with actual ETL logic
    duration = time.time() - start_time
    logger.info(f"Completed ETL phase: {phase} in {duration:.2f} seconds")
    return {"rows_extracted": 100, "rows_loaded": 100}  # Replace with actual counts

async def main(config: str, dry_run: bool, phase: str) -> None:
    global exit_code
    try:
        if phase:
            result = await run_etl_phase(phase)
        else:
            for p in ["extract", "transform", "load"]:
                result = await run_etl_phase(p)
        
        logger.info(f"Execution summary: {result}")
    except Exception as e:
        logger.error(f"ETL process failed: {e}")
        exit_code = 2

def signal_handler(sig, frame):
    global exit_code
    logger.info("Graceful shutdown initiated.")
    exit_code = 1
    asyncio.get_event_loop().stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Pipeline for Global Economic Indicators")
    parser.add_argument("--config", required=True, help="Path to the configuration file")
    parser.add_argument("--dry-run", action="store_true", help="Run the pipeline in dry run mode")
    parser.add_argument("--phase", help="Specify a single phase to run")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main(args.config, args.dry_run, args.phase))
    finally:
        loop.close()
        exit(exit_code)