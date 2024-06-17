import argparse

from lib.usable_versions_selection import UsableVersionSelection

# This script it to test versions (of subject)
# the version is considered usable (and saved within out/usable_buggy_versions)
# 1. if all its failing TCs execute its dedicated buggy line
# 2. if the coverage of each failing TC is measurable (no internal crash, etc.)
def main():
    parser = make_parser()
    args = parser.parse_args()

    subject = UsableVersionSelection(args.subject, args.verbose)
    subject.run()

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")
    return parser

if __name__ == "__main__":
    main()
