import argparse

from lib.mbfl_extraction import MBFLExtraction

# This script it to executes mutation testing on target versions
# then retrieves mbfl features on...
# 1. <number_of_lines_to_mutation_test> amount of randomly selected lines
# 2. with <max_mutants> amount of mutants on each selected lines
def main():
    parser = make_parser()
    args = parser.parse_args()

    subject = MBFLExtraction(
        args.subject, args.target_set_name, args.trial,
        args.verbose, args.past_trials, args.exclude_init_lines, # 2024-08-13 exclude lines executed on initialization
        args.parallel_cnt, args.dont_terminate_leftovers, # 2024-08-13 implement parallel mode
        args.remain_one_bug_per_line # 2024-08-16 implement flag for remaining one bug per line
    )
    subject.run()

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--target-set-name", type=str, help="Target set name that contains prerequisite data", required=True)
    parser.add_argument("--trial", type=str, help="Trial name", required=True) # 2024-08-07 add-mbfl
    parser.add_argument("--past-trials", type=str, nargs="+", help="list trial name from past to increment mbfl results")
    parser.add_argument("--exclude-init-lines", action="store_true", help="Option to exclude lines executed on initialization for mbfl") # 2024-08-13 exclude lines executed on initialization
    parser.add_argument("--parallel-cnt", type=int, default=0, help="Number of parallel runs during mbfl on single buggy version (0 to not use parallel count)") # 2024-08-13 implement parallel mode
    parser.add_argument("--dont-terminate-leftovers", action="store_true", help="Flag to turn of automatic termination on left overs during MBFL")
    parser.add_argument("--remain-one-bug-per-line", action="store_true", help="Flag to only use one bug per line") # 2024-08-16 implement flag for remaining one bug per line
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")
    return parser

if __name__ == "__main__":
    main()
