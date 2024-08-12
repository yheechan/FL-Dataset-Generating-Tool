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
    elif args.prerequisite_data:
        subject.prerequisite_data(args.removed_initialization_coverage)
    elif args.remove_versions_mbfl != None:
        if len(args.remove_versions_mbfl) != 0:
            subject.remove_versions_mbfl_meeting_criteria(args.remove_versions_mbfl)
    elif args.crashed_buggy_mutants:
        subject.crashed_buggy_mutants()

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--set-name", type=str, help="Set name", required=True)
    parser.add_argument("--output-csv", type=str, help="Output csv name", required=True)
    
    parser.add_argument("--usable-buggy-versions", action="store_true", help="Get test case statistics")
    parser.add_argument("--prerequisite-data", action="store_true", help="Get prerequisite data")
    parser.add_argument("--removed-initialization-coverage", action="store_true", help="Option to measure coverage difference") # 2024-08-12 measure distinct lines by failing TCs

    parser.add_argument("--remove-versions-mbfl", type=str, choices=["criteriaA", "criteriaB"], nargs="+", help="Remove versions based on MBFL criteria")
    
    parser.add_argument("--crashed-buggy-mutants", action="store_true", help="Analyze crashed buggy mutants")
    return parser

if __name__ == "__main__":
    main()
