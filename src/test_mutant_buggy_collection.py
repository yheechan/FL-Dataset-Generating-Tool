import argparse

# from include.subject_base import Subject
from lib.buggy_mutant_collection import BuggyMutantCollection
from version_bug_collection import VersionBugCollection

def main():
    parser = make_parser()
    args = parser.parse_args()

    subject = BuggyMutantCollection(args.subject)
    subject.run()

def make_parser():
    parser = argparse.ArgumentParser(description='Copy subject to working directory')
    parser.add_argument('--subject', type=str, help='Subject name', required=True)
    parser.add_argument('--stage', type=str, help='Stage name', required=True)
    parser.add_argument('--machine', type=str, help='Machine name', required=True)
    parser.add_argument('--core', type=str, help='Core name', required=True)
    parser.add_argument('--mutant-path', type=str, help='Mutant path', required=True)
    return parser

if __name__ == "__main__":
    main()
