import argparse

from lib.prerequisite_preparation import PrerequisitePreparation
from lib.slack import Slack
import time

# This script it to executes passing and failing tcs of versions
# then retrieves following prerequisite data:
# 1. coverage of each TCs (preprocessed to csv format)
# 2. lines executed by failing TCs (preprocessed to json format)
# 3. lines executed by passing TCs (preprocessed to json format)
# 4. line2functino mapping (preprocessed to json format)
def main():
    parser = make_parser()
    args = parser.parse_args()

    slack = Slack(channel_name="C0837SKQLK0", bot_name="prerequisite-data-preparer-bot")
    subject = PrerequisitePreparation(
        args.subject, args.experiment_name, args.version_limit, args.verbose
    )
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
    parser.add_argument("--version-limit", type=int, default=0, help="Limit the number of versions to be processed")
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")
    return parser

if __name__ == "__main__":
    main()
