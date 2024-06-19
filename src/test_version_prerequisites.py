import argparse

from lib.worker_stage03 import WorkerStage03

# This script it to test single version (of subject)
# in order to prepare prerequisite data for the version
# 1. coverage of each TCs (preprocessed to csv format)
# 2. lines executed by failing TCs (preprocessed to json format)
# 3. lines executed by passing TCs (preprocessed to json format)
# 4. line2functino mapping (preprocessed to json format)
def main():
    parser = make_parser()
    args = parser.parse_args()

    worker = WorkerStage03(
        args.subject, args.machine, args.core,
        args.version, args.need_configure,
        args.use_excluded_failing_tcs, args.exclude_ccts,
        args.passing_tcs_perc, args.failing_tcs_perc, args.verbose
    )
    worker.run()

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--machine", type=str, help="Machine name", required=True)
    parser.add_argument("--core", type=str, help="Core name", required=True)
    parser.add_argument("--version", type=str, help="Version name", required=True)
    parser.add_argument("--need-configure", action="store_true", help="Need configure")
    parser.add_argument("--use-excluded-failing-tcs", action="store_true", help="Use excluded failing tcs")
    parser.add_argument("--exclude-ccts", action="store_true", help="Exclude CCTs")
    parser.add_argument("--passing-tcs-perc", type=float, default=1.0, help="Percentage of passing tcs to use (default: 1.0, range: 0.0 ~ 1.0)")
    parser.add_argument("--failing-tcs-perc", type=float, default=1.0, help="Percentage of failing tcs to use (default: 1.0, range: 0.0 ~ 1.0)")
    parser.add_argument("--verbose", action="store_true", help="Verbose mode")
    return parser

if __name__ == "__main__":
    main()
