import argparse

from lib.worker_stage01 import WorkerStage01

# This script is to test single mutant (of subject)
# the mutant is considered buggy (and saved within out/buggy_mutants)
# if at least one test case fails
def main():
    parser = make_parser()
    args = parser.parse_args()

    worker = WorkerStage01(
        args.subject, args.experiment_name, args.machine, args.core,
        args.mutant_path, args.target_file_path, args.need_configure,
        args.last_mutant, args.verbose
    )
    worker.run()

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--experiment-name", type=str, help="Experiment name", required=True)
    parser.add_argument("--machine", type=str, help="Machine name", required=True)
    parser.add_argument("--core", type=str, help="Core name", required=True)
    parser.add_argument("--mutant-path", type=str, help="Mutant path", required=True)
    parser.add_argument("--target-file-path", type=str, help="Target file path", required=True)
    parser.add_argument("--need-configure", action="store_true", help="Need configure")
    parser.add_argument("--last-mutant", action="store_true", help="Last mutant")
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")
    return parser

if __name__ == "__main__":
    main()
