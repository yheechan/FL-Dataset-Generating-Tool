import argparse

from lib.sbfl_extraction import SBFLExtraction
from lib.slack import Slack
import time

# This script it to executes mutation testing on target versions
# then retrieves sbfl features
def main():
    parser = make_parser()
    args = parser.parse_args()

    slack = Slack(channel_name="C0837SKQLK0", bot_name="sbfl-feature-extractor-bot")
    subject = SBFLExtraction(args.subject, args.experiment_name, args.target_set_name, args.verbose)

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
    parser.add_argument("--target-set-name", type=str, help="Target set name that contains prerequisite data (select set from mbfl extractions results)", required=True)
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")
    return parser

if __name__ == "__main__":
    main()
