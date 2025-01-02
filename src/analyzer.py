import argparse

from analysis.analyze import Analyze
from lib.utils import list_of_ints

help_for_analysis_criteria = \
"""
*** Example:
    --validation-criteria 1,2,3

*** Validation criteria:
    1: [stage03] Analyze test cases and coverage statistics for all buggy versions resulting from prerequisite data preparation
    2: [stage05] Analyze MBFL results for all buggy versions resulting from MBFL feature extraction
    3: [stage05] Analyze probability that buggy line is within top-k percent based on sbfl suspiciousness scores
"""

# This script is to test mutants (of subject)
# the mutant is considered buggy (and saved within out/buggy_mutants)
# if at least one test case fails
def main():
    parser = make_parser()
    args = parser.parse_args()

    analyzer = Analyze(args.subject, args.experiment_name, verbose=args.verbose)
    analyzer.run(args.analysis_criteria, type_name=args.type_name)



def make_parser():
    parser = argparse.ArgumentParser(
        description="Analyze extracted data (i.e., prerequisite data, FL features, etc.) of a given subject",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    # parser.add_argument("--set-name", type=str, help="Set name", required=True)
    parser.add_argument("--experiment-name", type=str, help="Experiment name", required=True)
    parser.add_argument("--analysis-criteria", type=list_of_ints, help=help_for_analysis_criteria, required=True)
    parser.add_argument("--type-name", type=str, help="Type name", required=False)
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")

    return parser

if __name__ == "__main__":
    main()
