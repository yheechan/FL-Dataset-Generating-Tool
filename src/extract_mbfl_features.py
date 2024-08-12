import argparse

from lib.mbfl_extraction import MBFLExtraction

# This script it to executes mutation testing on target versions
# then retrieves mbfl features on...
# 1. <number_of_lines_to_mutation_test> amount of randomly selected lines
# 2. with <max_mutants> amount of mutants on each selected lines
def main():
    parser = make_parser()
    args = parser.parse_args()

    subject = MBFLExtraction(args.subject, args.target_set_name, args.trial, args.verbose, args.past_trials)
    subject.run()

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--target-set-name", type=str, help="Target set name that contains prerequisite data", required=True)
    parser.add_argument("--trial", type=str, help="Trial name", required=True) # 2024-08-07 add-mbfl
    parser.add_argument("--past-trials", type=str, nargs="+", help="list trial name from past to increment mbfl results")
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")
    return parser

if __name__ == "__main__":
    main()
