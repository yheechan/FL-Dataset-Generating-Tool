import argparse

from analysis.rank import Rank

# This script is to test mutants (of subject)
# the mutant is considered buggy (and saved within out/buggy_mutants)
# if at least one test case fails
def main():
    parser = make_parser()
    args = parser.parse_args()

    subject = Rank(args.subject, args.set_name, args.output_csv)

    if args.mbfl_features:
        subject.rank_mbfl_features(trialName=args.trial, noCCTs=args.no_ccts)
    elif args.sbfl_features:
        subject.rank_sbfl_features(noCCTs=args.no_ccts)

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--set-name", type=str, help="Set name", required=True)
    parser.add_argument("--output-csv", type=str, help="Output csv name", required=True)
    
    parser.add_argument("--mbfl-features", action="store_true", help="Get rank of MBFL features")
    parser.add_argument("--trial", type=str, help="Trial name")
    parser.add_argument("--no-ccts", action="store_true", help="Do not consider CCTs")
    parser.add_argument("--sbfl-features", action="store_true", help="Get rank of SBFL features")
    return parser

if __name__ == "__main__":
    main()
