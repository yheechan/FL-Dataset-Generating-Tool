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
        subject.remove_versions_mbfl_meeting_criteria(args.remove_versions_mbfl, args.trial)
    elif args.combine_mbfl_sbfl:
        assert args.combining_trials != None, f"combing trials is not given"
        subject.combine_mbfl_sbfl(args.combining_trials, noCCTs=args.no_ccts, doneRemotely=args.done_remotely) # 2024-08-19
    elif args.combine_mbfl_trials == True:
        assert args.past_trials != None, f"past trials is not given"
        subject.combine_mbfl_trials(args.past_trials, noCCTs=args.no_ccts)

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--set-name", type=str, help="Set name", required=True)
    
    parser.add_argument("--reduce-testsuite-size", type=int, default=0, help="Reduce test suite size (from usable_buggy_versions stage)")
    parser.add_argument("--appropriate-version-with-all-failing-tcs", action="store_true", help="Get appropriate versions with all failing test cases (from usable_buggy_versions stage)")
    parser.add_argument("--remove-versions-mbfl", type=str, choices=["criteriaA", "criteriaB"], nargs="+", help="Remove versions based on MBFL criteria")
    parser.add_argument("--trial", type=str, help="trial name")
    parser.add_argument("--combine-mbfl-sbfl", action="store_true", help="Combine MBFL and SBFL features (give set-name of SBFL features directory)")
    parser.add_argument("--combining-trials", type=str, nargs="+", help="trials to be combined") # 2024-08-19

    parser.add_argument("--combine-mbfl-trials", action="store_true", help="Combine mbfl results from multiple trials. ex: trial1 trial2") # 2024-08-07 add-mbfl
    parser.add_argument("--past-trials", type=str, nargs="+", help="Combine mbfl results from multiple trials. ex: trial1 trial2")
    parser.add_argument("--no-ccts", action="store_true", help="Do not consider CCTs")
    parser.add_argument("--done-remotely", action="store_true", help="If the task is done remotely")
    return parser

if __name__ == "__main__":
    main()
