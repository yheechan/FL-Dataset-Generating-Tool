import argparse

from lib.worker_stage04 import WorkerStage04

# This script it to test single version (of subject)
# in order to mbfl feature data for the version
def main():
    parser = make_parser()
    args = parser.parse_args()

    worker = WorkerStage04(
        args.subject, args.machine, args.core,
        args.version, args.trial, args.verbose, args.past_trials
    )
    worker.run()

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--machine", type=str, help="Machine name", required=True)
    parser.add_argument("--core", type=str, help="Core name", required=True)
    parser.add_argument("--version", type=str, help="Version name", required=True)
    parser.add_argument("--trial", type=str, help="Trial name", required=True) # 2024-08-07 add-mbfl
    parser.add_argument("--past-trials", type=str, nargs="+", help="list trial name from past to increment mbfl results")
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")
    return parser

if __name__ == "__main__":
    main()
