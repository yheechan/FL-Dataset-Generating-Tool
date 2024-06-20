import argparse

from analysis.analyze import Analyze

# This script is to test mutants (of subject)
# the mutant is considered buggy (and saved within out/buggy_mutants)
# if at least one test case fails
def main():
    parser = make_parser()
    args = parser.parse_args()

    subject = Analyze(args.subject, args.set_name, args.output_csv)

    if args.usable_buggy_versions:
        subject.usable_buggy_versions()
    elif args.reduce_testsuite_size != 0:
        subject.reduce_testsuite_size(args.reduce_testsuite_size)
    elif args.appropriate_version_with_all_failing_tcs:
        subject.appropriate_version_with_all_failing_tcs()
    elif args.prerequisite_data:
        subject.prerequisite_data()
    elif len(args.remove_versions_mbfl) != 0:
        subject.remove_versions_mbfl_meeting_criteria(args.remove_versions_mbfl)

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--set-name", type=str, help="Set name", required=True)
    parser.add_argument("--output-csv", type=str, help="Output csv name", required=True)
    
    parser.add_argument("--usable-buggy-versions", action="store_true", help="Get test case statistics")
    parser.add_argument("--reduce-testsuite-size", type=int, default=0, help="Reduce test suite size (from usable_buggy_versions stage)")
    parser.add_argument("--appropriate-version-with-all-failing-tcs", action="store_true", help="Get appropriate versions with all failing test cases (from usable_buggy_versions stage)")
    parser.add_argument("--prerequisite-data", action="store_true", help="Get prerequisite data")

    parser.add_argument("--remove-versions-mbfl", type=str, choices=["criteriaA", "criteriaB"], nargs="+", help="Remove versions based on MBFL criteria")
    return parser

if __name__ == "__main__":
    main()
