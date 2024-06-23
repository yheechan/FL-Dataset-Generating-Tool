import argparse

from analysis.reconstruct import Reconstruct

# This script is to test mutants (of subject)
# the mutant is considered buggy (and saved within out/buggy_mutants)
# if at least one test case fails
def main():
    parser = make_parser()
    args = parser.parse_args()

    subject = Reconstruct(args.subject, args.set_name)

    if args.reduce_testsuite_size != 0:
        subject.reduce_testsuite_size(args.reduce_testsuite_size)
    elif args.appropriate_version_with_all_failing_tcs:
        subject.appropriate_version_with_all_failing_tcs()
    elif args.remove_versions_mbfl:
        subject.remove_versions_mbfl_meeting_criteria(args.remove_versions_mbfl)
    elif args.combine_mbfl_sbfl:
        subject.combine_mbfl_sbfl()

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--set-name", type=str, help="Set name", required=True)
    
    parser.add_argument("--reduce-testsuite-size", type=int, default=0, help="Reduce test suite size (from usable_buggy_versions stage)")
    parser.add_argument("--appropriate-version-with-all-failing-tcs", action="store_true", help="Get appropriate versions with all failing test cases (from usable_buggy_versions stage)")

    parser.add_argument("--remove-versions-mbfl", type=str, choices=["criteriaA", "criteriaB"], nargs="+", help="Remove versions based on MBFL criteria")
    parser.add_argument("--combine-mbfl-sbfl", action="store_true", help="Combine MBFL and SBFL features (give set-name of SBFL features directory)")
    return parser

if __name__ == "__main__":
    main()
