import argparse

# from include.subject_base import Subject
from lib.worker_stage01 import WorkerStage01

def main():
    parser = make_parser()
    args = parser.parse_args()

    worker = WorkerStage01(
        args.subject, args.machine, args.core,
        args.mutant_path, args.target_file_path, args.need_configure
    )
    worker.run()

def make_parser():
    parser = argparse.ArgumentParser(description='Copy subject to working directory')
    parser.add_argument('--subject', type=str, help='Subject name', required=True)
    parser.add_argument('--machine', type=str, help='Machine name', required=True)
    parser.add_argument('--core', type=str, help='Core name', required=True)
    parser.add_argument('--mutant-path', type=str, help='Mutant path', required=True)
    parser.add_argument('--target-file-path', type=str, help='Target file path', required=True)
    parser.add_argument('--need-configure', action='store_true', help='Need configure')
    return parser

if __name__ == "__main__":
    main()
