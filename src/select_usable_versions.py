import argparse

from lib.usable_versions_selection import UsableVersionSelection
from lib.slack import Slack
import time


# This script it to test versions (of subject)
# the version is considered usable (and saved within out/usable_buggy_versions)
# 1. if all its failing TCs execute its dedicated buggy line
# 2. if the coverage of each failing TC is measurable (no internal crash, etc.)
def main():
    parser = make_parser()
    args = parser.parse_args()

    slack = Slack(channel_name="C0837SKQLK0", bot_name="usable-version-selecting-bot")
    subject = UsableVersionSelection(args.subject, args.experiment_name, args.verbose)
    start_time = time.time()
    slack.send_message(f"Worker started at {start_time}")
    subject.run()
    end_time = time.time()

    sec = end_time - start_time
    minute = sec / 60
    hour = minute / 60

    slack.send_message(f"Worker finished in:\n\tsec: {sec}\n\tmin: {minute}\n\thour: {hour}")

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--experiment-name", type=str, help="Experiment name", required=True)
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")
    return parser

if __name__ == "__main__":
    main()
