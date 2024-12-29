import argparse

from analysis.validate import Validate
from lib.utils import list_of_ints

help_for_validation_criteria = \
"""
*** Example:
    --validation-criteria 1,2,3

*** Validation criteria:
    0: Validate all existing validation criteria
    1: [stage03] Validate that all buggy versions resulting from prerequisite data preparation stage consists 1 buggy line in line_info table
    2: [stage03] Validate that coverage for all test cases from all buggy versions resulting from prerequisite data preparation has been recorded on tc_info table
    3: [stage03] Validate that test cases and coverage statistics for all buggy versions resulting from prerequisite data preparation has been recorded on bug_info table
    4: [stage03] Validate that all failing test cases from all buggy versions resulting from prerequisite data executes the buggy line
    5: [stage03] Validate that for each bug_idx in bug_info with prerequisites IS TRUE:
            1. num_failing_tcs > 0 and num_passing_tcs > 0.
            2. The number of rows in tc_info with tc_result='fail' matches num_failing_tcs.
            3. The number of rows in tc_info with tc_result='pass' matches num_passing_tcs.
    6: [stage03] Validate that all lines_executed_by_failing_tc.json and line2function.json file are available for all buggy versions resulting from prerequisite data preparation
    7: [stage04] Validate the following for all bug_idx in bug_info with sbfl IS TRUE:
            1. Columns ep, np, ef, nf, cct_ep, and cct_np in line_info are not NULL.
            2. ep + np = num_passing_tcs in bug_info.
            3. ef + nf = num_failing_tcs in bug_info.
            4. cct_ep + cct_np = num_ccts in bug_info.
    8: [stage05] Validate the following columns in line_info table for all bug_idx in bug_info with mbfl IS TRUE:
            1. for_sbfl_ranked_mbfl_asc is TRUE
            2. for_sbfl_ranked_mbfl_desc is TRUE
            3. for_random_mbfl is TRUE
    9: [stage05] Validate number of mutations generated on buggy line is greater than 0 for all bug_idx in bug_info with mbfl IS TRUE
    10: [stage05] Validate the following for all bug_idx in bug_info with mbfl IS TRUE:
            1. Columns f2p, p2f, f2f, p2p, p2f_cct, and p2p_cct in mutation_info are not NULL.
            2. f2p + f2f = num_failing_tcs in bug_info.
            3. p2f + p2p = num_passing_tcs in bug_info.
            4. p2f_cct + p2p_cct = num_ccts in bug_info.

"""

# This script is to test mutants (of subject)
# the mutant is considered buggy (and saved within out/buggy_mutants)
# if at least one test case fails
def main():
    parser = make_parser()
    args = parser.parse_args()

    validator = Validate(args.subject, args.experiment_name)
    validator.run(args.validation_criteria)
    

    # if args.validate_usable_buggy_versions:
    #     subject.validate_usable_buggy_versions()
    # elif args.validate_prerequisite_data:
    #     subject.validate_prerequisite_data()
    # elif args.validate_mbfl_features:
    #     subject.validate_mbfl_features(args.trial)
    # elif args.validate_sbfl_features:
    #     subject.validate_sbfl_features()
    # elif args.validate_fl_features:
    #     subject.validate_fl_features()

def make_parser():
    parser = argparse.ArgumentParser(
        description="Validate extracted data (i.e., prerequisite data, FL features, etc.) of a given subject",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--subject", type=str, help="Subject name", required=True)
    parser.add_argument("--experiment-name", type=str, help="Experiment name", required=True)
    parser.add_argument("--validation-criteria", type=list_of_ints, help=help_for_validation_criteria, required=True)
    # parser.add_argument("--set-name", type=str, help="Set name", required=True)
    
    # parser.add_argument("--validate-usable-buggy-versions", action="store_true", help="Validate usable buggy versions")
    # parser.add_argument("--validate-prerequisite-data", action="store_true", help="Validate prerequisite data")
    # parser.add_argument("--validate-mbfl-features", action="store_true", help="Validate MBFL feature")
    # parser.add_argument("--trial", type=str, help="Trial Name")
    # parser.add_argument("--validate-sbfl-features", action="store_true", help="Validate SBFL feature")
    # parser.add_argument("--validate-fl-features", action="store_true", help="Validate FL feature")
    return parser

if __name__ == "__main__":
    main()