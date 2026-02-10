import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
STEPS = [
    "validate_data.py",
    "find_PnL.py",
]

def main():
    for name in STEPS:
        path = SCRIPT_DIR / name
        if not path.exists():
            print(f"Missing script: {path}", file=sys.stderr)
            sys.exit(1)
        print(f"Running {name} ...")
        r = subprocess.run([sys.executable, str(path)], cwd=SCRIPT_DIR)
        if r.returncode != 0:
            print(f"{name} failed with exit code {r.returncode}", file=sys.stderr)
            sys.exit(r.returncode)
    print("Done.")

if __name__ == "__main__":
    main()
