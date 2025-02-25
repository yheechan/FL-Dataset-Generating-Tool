import argparse

from analysis.analyze import Analyze
from lib.utils import list_of_ints
from lib.slack import Slack
import time

help_for_analysis_criteria = \
"""
*** Example:
    --validation-criteria 1,2,3

*** Validation criteria:
    1: [stage03] Analyze test cases and coverage statistics for all buggy versions resulting from prerequisite data preparation
    2: [stage05] Analyze MBFL results for all buggy versions resulting from MBFL feature extraction and save the final results to file system for ML learning
    3: [stage05] Analyze probability that buggy line is within top-k percent based on sbfl suspiciousness scores
    4: [stage05] SBFL rank of buggy lines for all buggy versions resulting from MBFL feature extraction
    5: [stage05] Download SBFL features for all buggy versions
    6: [stage05] Generate figures for mbfl score and MBFL feature extraction time for subjects and analysis types below
    7: [stage05] Write the statistical numbers of mutations
"""

# This script is to test mutants (of subject)
# the mutant is considered buggy (and saved within out/buggy_mutants)
# if at least one test case fails
def main():
    parser = make_parser()
    args = parser.parse_args()

    slack = Slack(channel_name="C0837SKQLK0", bot_name="analyzer-bot")
    analyzer = Analyze(args.subject, args.experiment_name, verbose=args.verbose)

    start_time = time.time()
    slack.send_message(f"Worker started at {start_time}")
    analyzer.run(args.analysis_criteria, type_name=args.type_name, batch_size=args.batch_size)

    end_time = time.time()

    sec = end_time - start_time
    minute = sec / 60
    hour = minute / 60

    slack.send_message(f"Worker finished in:\n\tsec: {sec}\n\tmin: {minute}\n\thour: {hour}")



def make_parser():
    parser = argparse.ArgumentParser(
        description="Analyze extracted data (i.e., prerequisite data, FL features, etc.) of a given subject",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--experiment-name", type=str, help="Experiment name", required=True)
    parser.add_argument("--analysis-criteria", type=list_of_ints, help=help_for_analysis_criteria, required=True)
    parser.add_argument("--type-name", type=str, help="Type name", required=False)
    parser.add_argument("--batch-size", type=str, help="Batch size", required=False)
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")

    return parser

if __name__ == "__main__":
    main()
