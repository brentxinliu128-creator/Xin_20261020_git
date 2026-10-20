import argparse
import os
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Finds .py files older than a given number of days.")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to search (default: current directory)")
    parser.add_argument("-d", "--days", type=int, default=30, help="Age threshold in days (default: 30)")
    parser.add_argument("-r", "--show-age", action="store_true", help="Show each file's age in days")
    args = parser.parse_args()

    cutoff = time.time() - args.days * 86400
    found = 0

    for root, dirs, files in os.walk(args.directory):
        for name in files:
            if not name.endswith(".py"):
                continue
            path = Path(root) / name
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            if mtime < cutoff:
                age_days = (time.time() - mtime) / 86400
                if args.show_age:
                    print(f"{path}  ({age_days:.1f} days)")
                else:
                    print(path)
                found += 1

    print(f"\n{found} .py file(s) older than {args.days} day(s) found.")


if __name__ == "__main__":
    main()