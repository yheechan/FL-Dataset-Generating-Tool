import argparse

from lib.worker_stage02 import WorkerStage02

# This script it to test single version (of subject)
# the version is considered usable (and saved within out/usable_buggy_versions)
# 1. if all its failing TCs execute its dedicated buggy line
# 2. if the coverage of each failing TC is measurable (no internal crash, etc.)
def main():
    parser = make_parser()
    args = parser.parse_args()

    worker = WorkerStage02(
        args.subject, args.experiment_name, args.machine, args.core,
        args.version, args.need_configure,
        args.last_version, args.verbose
    )
    worker.run()

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--experiment-name", type=str, help="Experiment name", required=True)
    parser.add_argument("--machine", type=str, help="Machine name", required=True)
    parser.add_argument("--core", type=str, help="Core name", required=True)
    parser.add_argument("--version", type=str, help="Version name", required=True)
    parser.add_argument("--need-configure", action="store_true", help="Need configure")
    parser.add_argument("--last-version", action="store_true", help="Last version")
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")
    return parser

if __name__ == "__main__":
    main()
