import argparse

from lib.buggy_mutant_collection import BuggyMutantCollection
from lib.slack import Slack
import time


# This script is to test mutants (of subject)
# the mutant is considered buggy (and saved within out/buggy_mutants)
# if at least one test case fails
def main():
    parser = make_parser()
    args = parser.parse_args()

    slack = Slack(channel_name="C0837SKQLK0", bot_name="buggy-mutants-collecting-bot")
    subject = BuggyMutantCollection(args.subject, args.experiment_name, args.verbose)
    start_time = time.time()
    slack.send_message(f"Worker started at {start_time}")
    if args.save_crashed_buggy_mutants == False: # 2024-08-09 save-crashed-buggy-mutants
        subject.run()
    else:
        subject.save_crashed_buggy_mutants()
    end_time = time.time()

    sec = end_time - start_time
    minute = sec / 60
    hour = minute / 60

    slack.send_message(f"Worker finished in:\n\tsec: {sec}\n\tmin: {minute}\n\thour: {hour}")

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--experiment-name", type=str, help="Experiment name", required=True)
    parser.add_argument("--save-crashed-buggy-mutants", action="store_true", help="Flag to save mutants within crashed_buggy_mutants directory") # 2024-08-09 save-crashed-buggy-mutants
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")
    return parser

if __name__ == "__main__":
    main()
