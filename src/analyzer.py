import argparse

from analysis.analyze import Analyze

# This script is to test mutants (of subject)
# the mutant is considered buggy (and saved within out/buggy_mutants)
# if at least one test case fails
def main():
    parser = make_parser()
    args = parser.parse_args()

    subject = Analyze(args.subject, args.set_name, args.output_csv)

    if args.tc_stats:
        subject.testcase_statistics()
    elif args.reduce_testsuite_size != 0:
        subject.reduce_testsuite_size(args.reduce_testsuite_size)
    elif args.appropriate_version_with_all_failing_tcs:
        subject.appropriate_version_with_all_failing_tcs()

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--set-name", type=str, help="Set name", required=True)
    parser.add_argument("--output-csv", type=str, help="Output csv name", required=True)
    
    parser.add_argument("--tc-stats", action="store_true", help="Get test case statistics")
    parser.add_argument("--reduce-testsuite-size", type=int, default=0, help="Reduce test suite size")
    parser.add_argument("--appropriate-version-with-all-failing-tcs", action="store_true", help="Get appropriate versions with all failing test cases")
    return parser

if __name__ == "__main__":
    main()
