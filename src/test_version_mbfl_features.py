import argparse

from lib.worker_stage05 import WorkerStage05

# This script it to test single version (of subject)
# in order to mbfl feature data for the version
def main():
    parser = make_parser()
    args = parser.parse_args()

    worker = WorkerStage05(
        args.subject, args.experiment_name,
        args.machine, args.core,
        args.version, args.trial, args.verbose,
        args.past_trials, args.exclude_init_lines, # 2024-08-13 exclude lines executed on initialization
        args.parallel_cnt, args.parallel_mode # 2024-08-13 implement parallel mode
    )
    worker.run()

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--experiment-name", type=str, help="Experiment name", required=True)
    parser.add_argument("--machine", type=str, help="Machine name", required=True)
    parser.add_argument("--core", type=str, help="Core name", required=True)
    parser.add_argument("--version", type=str, help="Version name", required=True)
    parser.add_argument("--trial", type=str, help="Trial name", required=True) # 2024-08-07 add-mbfl
    parser.add_argument("--past-trials", type=str, nargs="+", help="list trial name from past to increment mbfl results")
    parser.add_argument("--exclude-init-lines", action="store_true", help="Option to exclude lines executed on initialization for mbfl") # 2024-08-13 exclude lines executed on initialization
    parser.add_argument("--parallel-cnt", type=int, default=0, help="Number of parallel runs during mbfl on single buggy version") # 2024-08-13 implement parallel mode
    parser.add_argument("--parallel-mode", action="store_true", help="Automatically set within program when <parallel-cnt> option is given (NOT FOR USERS")
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")
    return parser

if __name__ == "__main__":
    main()
