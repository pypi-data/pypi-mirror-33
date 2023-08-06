import argparse
import os
import sys
from pathlib import Path  # noqa - This is used in the `exec` call.


def main():
    parser = argparse.ArgumentParser(prog="prs", description="Add some Python to your shell life.")
    parser.add_argument("script", metavar="CODE", type=str, help="The code to run.")

    args = parser.parse_args()

    if os.isatty(0):
        print("prs expects stuff to be piped to it.", file=sys.stderr)
        sys.exit(1)

    # Read stdin.
    i = sys.stdin.readlines()

    # Strip final newline.
    i = [x[:-1] for x in i]

    scope = globals().copy()
    scope["i"] = i

    exec(args.script, scope)

    if "o" not in scope:
        print("prs expects its output in a variable called `o`.", file=sys.stderr)
        sys.exit(1)

    result = scope["o"]

    if isinstance(result, list) or isinstance(result, tuple):
        for l in result:
            print(l)
    else:
        print(str(result))
