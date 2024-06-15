import argparse

# from include.subject_base import Subject
from lib.buggy_mutant_collection import BuggyMutantCollection

def main():
    parser = make_parser()
    args = parser.parse_args()

    subject = BuggyMutantCollection(args.subject)
    subject.run()

def make_parser():
    parser = argparse.ArgumentParser(description='Copy subject to working directory')
    parser.add_argument('--subject', type=str, help='Subject name', required=True)
    return parser

if __name__ == "__main__":
    main()
