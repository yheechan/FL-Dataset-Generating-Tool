import argparse

from lib.worker_stage05 import WorkerStage05

# This script it to test single version (of subject)
# in order to sbfl feature data for the version
def main():
    parser = make_parser()
    args = parser.parse_args()

    worker = WorkerStage05(
        args.subject, args.machine, args.core,
        args.version, args.verbose
    )
    worker.run()

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--machine", type=str, help="Machine name", required=True)
    parser.add_argument("--core", type=str, help="Core name", required=True)
    parser.add_argument("--version", type=str, help="Version name", required=True)
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")
    return parser

if __name__ == "__main__":
    main()
