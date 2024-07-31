import argparse

from ml.postprocessor import Postprocessor

# This script is to test mutants (of subject)
# the mutant is considered buggy (and saved within out/buggy_mutants)
# if at least one test case fails
def main():
    parser = make_parser()
    args = parser.parse_args()

    if args.postprocess_fl_features:
        postprocessor = Postprocessor(args.subject, args.set_name)
        postprocessor.run()

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--set-name", type=str, help="Set name", required=True)

    parser.add_argument("--postprocess-fl-features", action="store_true", help="Formulate FL dataset with features for machine learning.")

    return parser

if __name__ == "__main__":
    main()
