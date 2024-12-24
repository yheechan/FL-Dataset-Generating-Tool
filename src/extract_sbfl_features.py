import argparse

from lib.sbfl_extraction import SBFLExtraction

# This script it to executes mutation testing on target versions
# then retrieves sbfl features
def main():
    parser = make_parser()
    args = parser.parse_args()

    subject = SBFLExtraction(args.subject, args.target_set_name, args.verbose)
    subject.run()

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--experiment-name", type=str, help="Experiment name", required=True)
    parser.add_argument("--target-set-name", type=str, help="Target set name that contains prerequisite data (select set from mbfl extractions results)", required=True)
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")
    return parser

if __name__ == "__main__":
    main()
