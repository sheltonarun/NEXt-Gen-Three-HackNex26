import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent   # HackNex26/
SCRIPTS_DIR = ROOT / "outputs" / "scripts"


def save_script(code: str, name: str) -> Path:
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    path = SCRIPTS_DIR / f"{name}.py"
    path.write_text(code, encoding="utf-8")
    return path


def run_script(path, timeout: int = 30):
    """Run a script in a fresh process from the repo root.
    Returns (ok, stdout_or_error)."""
    try:
        r = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True, text=True, timeout=timeout, cwd=ROOT,
        )
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    if r.returncode != 0:
        return False, r.stderr.strip()
    return True, r.stdout.strip()


def parse_number(text: str):
    """Take the last line of output as the answer."""
    last = text.strip().splitlines()[-1]
    return float(last.replace(",", "").replace("$", "").replace("€", "").strip())