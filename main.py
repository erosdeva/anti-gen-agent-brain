"""
Unified entrypoint to run both the memory agent API (agent.py)
and the Streamlit dashboard (dashboard.py) in a single command.

Usage:
    python main.py

Optional arguments:
    python main.py \
        --watch ./inbox \
        --agent-port 8888 \
        --dashboard-port 8501 \
        --consolidate-every 30
"""

import argparse
import os
import signal
import subprocess
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run memory agent and dashboard together",
    )
    parser.add_argument(
        "--watch",
        default="./inbox",
        help="Folder to watch for new files (default: ./inbox)",
    )
    parser.add_argument(
        "--agent-port",
        type=int,
        default=8888,
        help="HTTP API port for agent.py (default: 8888)",
    )
    parser.add_argument(
        "--dashboard-port",
        type=int,
        default=8501,
        help="Port for Streamlit dashboard (default: 8501)",
    )
    parser.add_argument(
        "--consolidate-every",
        type=int,
        default=30,
        help="Consolidation interval in minutes (default: 30)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    project_root = Path(__file__).resolve().parent

    # Environment / working directory
    os.chdir(project_root)

    python_exe = sys.executable or "python"

    # Start the agent API
    agent_cmd = [
        python_exe,
        "agent.py",
        "--watch",
        args.watch,
        "--port",
        str(args.agent_port),
        "--consolidate-every",
        str(args.consolidate_every),
    ]

    print(f"Starting agent: {' '.join(agent_cmd)}")
    agent_proc = subprocess.Popen(
        agent_cmd,
        cwd=project_root,
    )

    # Start the Streamlit dashboard
    dashboard_cmd = [
        python_exe,
        "-m",
        "streamlit",
        "run",
        "dashboard.py",
        "--server.port",
        str(args.dashboard_port),
    ]

    print(f"Starting dashboard: {' '.join(dashboard_cmd)}")
    dashboard_proc = subprocess.Popen(
        dashboard_cmd,
        cwd=project_root,
    )

    # Handle shutdown: propagate signals, wait for children
    def handle_signal(signum, frame):
        print(f"\nReceived signal {signum}, shutting down children...")
        for proc in (agent_proc, dashboard_proc):
            if proc.poll() is None:
                try:
                    proc.terminate()
                except Exception:
                    pass

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    # Wait for both processes to finish
    try:
        exit_codes = []
        for proc in (agent_proc, dashboard_proc):
            exit_codes.append(proc.wait())
        # If either failed, propagate non-zero exit
        sys.exit(max(exit_codes))
    except KeyboardInterrupt:
        handle_signal(signal.SIGINT, None)
        sys.exit(130)


if __name__ == "__main__":
    main()

