import argparse
import asyncio
import logging
import signal
import sys
from typing import Any, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PipelineOrchestrator:
    async def run(self, phase: str, dry_run: bool) -> Dict[str, Any]:
        # Placeholder for actual implementation
        logger.info(f"Running phase: {phase} with dry_run={dry_run}")
        return {"rows_extracted": 0, "rows_loaded": 0, "errors": []}

async def main(config_path: str, dry_run: bool, phase: str) -> None:
    orchestrator = PipelineOrchestrator()
    execution_summary = {"phase_durations": {}, "rows_extracted": 0, "rows_loaded": 0, "errors": []}

    try:
        for p in phase.split(','):
            logger.info(f"Starting phase: {p}")
            phase_duration = await orchestrator.run(p, dry_run)
            execution_summary["phase_durations"][p] = phase_duration
            execution_summary["rows_extracted"] += phase_duration["rows_extracted"]
            execution_summary["rows_loaded"] += phase_duration["rows_loaded"]
            execution_summary["errors"].extend(phase_duration["errors"])
            logger.info(f"Completed phase: {p}")

        logger.info(f"Execution Summary: {execution_summary}")

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(2)

def signal_handler(sig: int, frame: Any) -> None:
    logger.info("Graceful shutdown initiated.")
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parser = argparse.ArgumentParser(description="Global Economic Indicators ETL Pipeline")
    parser.add_argument("--config", type=str, required=True, help="Path to the configuration file")
    parser.add_argument("--dry-run", action="store_true", help="Run the pipeline in dry run mode")
    parser.add_argument("--phase", type=str, choices=["extract", "transform", "validate", "load", "all"], required=True, help="Phase to run")

    args = parser.parse_args()
    asyncio.run(main(args.config, args.dry_run, args.phase))