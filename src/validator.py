import argparse

from analysis.validate import Validate

# This script is to test mutants (of subject)
# the mutant is considered buggy (and saved within out/buggy_mutants)
# if at least one test case fails
def main():
    parser = make_parser()
    args = parser.parse_args()

    subject = Validate(args.subject, args.set_name)

    if args.validate_usable_buggy_versions:
        subject.validate_usable_buggy_versions()
    elif args.validate_prerequisite_data:
        subject.validate_prerequisite_data()
    elif args.validate_mbfl_features:
        subject.validate_mbfl_features(args.trial)
    elif args.validate_sbfl_features:
        subject.validate_sbfl_features()
    elif args.validate_fl_features:
        subject.validate_fl_features()

def make_parser():
    parser = argparse.ArgumentParser(description="Copy subject to working directory")
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--set-name", type=str, help="Set name", required=True)
    
    parser.add_argument("--validate-usable-buggy-versions", action="store_true", help="Validate usable buggy versions")
    parser.add_argument("--validate-prerequisite-data", action="store_true", help="Validate prerequisite data")
    parser.add_argument("--validate-mbfl-features", action="store_true", help="Validate MBFL feature")
    parser.add_argument("--trial", type=str, help="Trial Name")
    parser.add_argument("--validate-sbfl-features", action="store_true", help="Validate SBFL feature")
    parser.add_argument("--validate-fl-features", action="store_true", help="Validate FL feature")
    return parser

if __name__ == "__main__":
    main()
