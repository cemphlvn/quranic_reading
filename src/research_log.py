"""
Research Log System

Traceable, append-only logging for scientific rigor.
Each experiment gets a unique ID and is logged to JSONL format.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict
import hashlib


LOG_PATH = Path("logs/research_log.jsonl")
COUNTER_PATH = Path("logs/.counter")


def get_next_id() -> str:
    """Get next experiment ID."""
    if COUNTER_PATH.exists():
        count = int(COUNTER_PATH.read_text().strip())
    else:
        count = 0
    count += 1
    COUNTER_PATH.parent.mkdir(exist_ok=True)
    COUNTER_PATH.write_text(str(count))
    return f"EXP_{count:04d}"


@dataclass
class ExperimentLog:
    """Single experiment log entry."""
    id: str
    timestamp: str
    encoding: str
    scope: str
    description: str

    # Input data hash for reproducibility
    data_hash: str

    # Results
    metrics: Dict[str, Any]
    null_test: Optional[Dict[str, Any]]
    control_test: Optional[Dict[str, Any]]

    # Interpretation
    interpretation: str
    status: str  # L1_TESTED, L2_CONTROLLED, L3_REPLICATED, L4_INTERPRETED

    # Traceability
    script: str
    git_commit: Optional[str]
    parent_exp: Optional[str]  # If this builds on previous experiment


def get_git_commit() -> Optional[str]:
    """Get current git commit hash."""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=Path(__file__).parent.parent
        )
        return result.stdout.strip()[:8] if result.returncode == 0 else None
    except:
        return None


def compute_data_hash(data: str) -> str:
    """Compute hash of input data for reproducibility."""
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def log_experiment(
    encoding: str,
    scope: str,
    description: str,
    data_sample: str,
    metrics: Dict[str, Any],
    null_test: Optional[Dict[str, Any]] = None,
    control_test: Optional[Dict[str, Any]] = None,
    interpretation: str = "",
    status: str = "L1_TESTED",
    script: str = "",
    parent_exp: Optional[str] = None,
) -> str:
    """
    Log an experiment. Returns experiment ID.

    Example:
        exp_id = log_experiment(
            encoding="E8_solar",
            scope="full",
            description="Solar/lunar encoding on full Quran",
            data_sample=quran_text[:1000],
            metrics={"density": 0.37, "z_score": -25.06},
            status="L2_CONTROLLED"
        )
    """
    exp_id = get_next_id()

    entry = ExperimentLog(
        id=exp_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        encoding=encoding,
        scope=scope,
        description=description,
        data_hash=compute_data_hash(data_sample),
        metrics=metrics,
        null_test=null_test,
        control_test=control_test,
        interpretation=interpretation,
        status=status,
        script=script,
        git_commit=get_git_commit(),
        parent_exp=parent_exp,
    )

    # Append to log
    LOG_PATH.parent.mkdir(exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(asdict(entry), default=str) + "\n")

    print(f"Logged: {exp_id} | {encoding} | {status}")
    return exp_id


def read_log() -> list:
    """Read all log entries."""
    if not LOG_PATH.exists():
        return []
    entries = []
    with open(LOG_PATH) as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))
    return entries


def get_experiment(exp_id: str) -> Optional[dict]:
    """Get specific experiment by ID."""
    for entry in read_log():
        if entry["id"] == exp_id:
            return entry
    return None


def print_log_summary():
    """Print summary of research log."""
    entries = read_log()
    if not entries:
        print("No experiments logged yet.")
        return

    print(f"\nResearch Log: {len(entries)} experiments")
    print("="*70)
    print(f"{'ID':<10} {'Encoding':<15} {'Status':<15} {'Timestamp':<25}")
    print("-"*70)

    for e in entries[-20:]:  # Last 20
        print(f"{e['id']:<10} {e['encoding']:<15} {e['status']:<15} {e['timestamp'][:19]}")

    if len(entries) > 20:
        print(f"... and {len(entries) - 20} more")


if __name__ == "__main__":
    print_log_summary()
