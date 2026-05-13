import argparse
import asyncio
import logging
import signal
import sys
import time
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    async def run(self, phase: str, dry_run: bool) -> dict:
        start_time = time.time()
        rows_extracted = 0
        rows_loaded = 0
        status = "success"
        error_message = ""

        try:
            if phase in ["extract", "all"]:
                # Simulate extraction logic
                rows_extracted = 1000  # Placeholder for actual extraction logic
                logger.info(f"Extracted {rows_extracted} rows.")

            if phase in ["load", "all"]:
                # Simulate loading logic
                rows_loaded = 1000  # Placeholder for actual loading logic
                logger.info(f"Loaded {rows_loaded} rows.")

        except Exception as e:
            status = "failed"
            error_message = str(e)
            logger.error(f"Error during {phase}: {error_message}")

        duration = time.time() - start_time
        logger.info(f"Phase '{phase}' completed in {duration:.2f} seconds.")
        return {
            "rows_extracted": rows_extracted,
            "rows_loaded": rows_loaded,
            "status": status,
            "error_message": error_message,
            "duration": duration
        }

async def main(config_path: str, dry_run: bool, phase: str) -> int:
    orchestrator = PipelineOrchestrator()
    summary = await orchestrator.run(phase, dry_run)

    logger.info(f"Execution Summary: {summary}")
    if summary["status"] == "failed":
        return 2
    elif summary["rows_extracted"] == 0 or summary["rows_loaded"] == 0:
        return 1
    return 0

def signal_handler(sig: int, frame: Optional[signal.FrameType]) -> None:
    logger.info("Graceful shutdown initiated.")
    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Global Economic Indicators ETL Pipeline")
    parser.add_argument("--config", type=str, required=True, help="Path to the configuration file.")
    parser.add_argument("--dry-run", action="store_true", help="Run the pipeline in dry run mode.")
    parser.add_argument("--phase", type=str, choices=["extract", "transform", "validate", "load", "all"], required=True, help="Phase to execute.")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    exit_code = asyncio.run(main(args.config, args.dry_run, args.phase))
    sys.exit(exit_code)