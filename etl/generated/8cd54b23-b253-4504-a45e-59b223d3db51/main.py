import argparse
import asyncio
import logging
import signal
import sys
import time
from typing import Any, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    async def run(self, phase: str, dry_run: bool) -> Dict[str, Any]:
        # Simulate phase execution
        start_time = time.time()
        logger.info(f"Starting phase: {phase}")
        await asyncio.sleep(1)  # Simulate work
        duration = time.time() - start_time
        rows_processed = 100  # Simulated value
        errors = []  # Simulated value
        logger.info(f"Completed phase: {phase} in {duration:.2f} seconds")
        return {"duration": duration, "rows_processed": rows_processed, "errors": errors}

async def main(config_path: str, dry_run: bool, phase: str) -> int:
    orchestrator = PipelineOrchestrator()
    total_errors = []
    total_rows = 0
    phases = phase.split(',') if phase != 'all' else ['extract', 'transform', 'validate', 'load']

    for phase in phases:
        result = await orchestrator.run(phase, dry_run)
        total_rows += result['rows_processed']
        total_errors.extend(result['errors'])

    logger.info(f"Execution Summary: Total Rows Processed: {total_rows}, Errors: {len(total_errors)}")
    if total_errors:
        return 1  # Partial failure
    return 0  # Success

def signal_handler(sig: int, frame: Any) -> None:
    logger.info("Graceful shutdown initiated.")
    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Global Economic Indicators ETL Pipeline")
    parser.add_argument("--config", type=str, required=True, help="Path to the configuration file")
    parser.add_argument("--dry-run", action="store_true", help="Run the pipeline in dry run mode")
    parser.add_argument("--phase", type=str, choices=["extract", "transform", "validate", "load", "all"], default="all", help="Phase to execute")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        exit_code = asyncio.run(main(args.config, args.dry_run, args.phase))
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(2)