import argparse

from lib.prerequisite_preparation import PrerequisitePreparation

# This script it to executes passing and failing tcs of versions
# then retrieves following prerequisite data:
# 1. coverage of each TCs (preprocessed to csv format)
# 2. lines executed by failing TCs (preprocessed to json format)
# 3. lines executed by passing TCs (preprocessed to json format)
# 4. line2functino mapping (preprocessed to json format)
def main():
    parser = make_parser()
    args = parser.parse_args()

    subject = PrerequisitePreparation(
        args.subject, args.target_set_name,
        args.use_excluded_failing_tcs,
        args.passing_tcs_perc, args.failing_tcs_perc, args.verbose
    )
    subject.run()

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--target-set-name", type=str, help="Target set name to extract prerequisite data (ex: usable_buggy_versions-reduced)", required=True)
    parser.add_argument("--use-excluded-failing-tcs", action="store_true", help="Use excluded failing tcs")
    parser.add_argument("--passing-tcs-perc", type=float, default=1.0, help="Percentage of passing tcs to use (default: 1.0, range: 0.0 ~ 1.0)")
    parser.add_argument("--failing-tcs-perc", type=float, default=1.0, help="Percentage of failing tcs to use (default: 1.0, range: 0.0 ~ 1.0)")
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")
    return parser

if __name__ == "__main__":
    main()
