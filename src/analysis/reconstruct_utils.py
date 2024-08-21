import subprocess as sp
import csv

from analysis.rank_utils import *

# ++++++++++++++++++++++++++++++++++++++++++++++
# +++++++ Combine SBFL and MBFL features +++++++
# ++++++++++++++++++++++++++++++++++++++++++++++

def copy_buggy_code_file(bug_id, dir_path, bug_code_filename, target_file_name, root_dest_dir):
    buggy_code_file_per_bug_version_dir = root_dest_dir / "buggy_code_file_per_bug_version"
    if not buggy_code_file_per_bug_version_dir.exists():
        buggy_code_file_per_bug_version_dir.mkdir(parents=True, exist_ok=True)
    

    buggy_code_file_dir = dir_path / "buggy_code_file" / bug_code_filename
    assert buggy_code_file_dir.exists(), f"Buggy code file {buggy_code_file_dir} does not exist"

    dest_dir = buggy_code_file_per_bug_version_dir / bug_id
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_file = dest_dir / target_file_name
    sp.check_call(f"cp {buggy_code_file_dir} {dest_file}", shell=True)

def copy_buggy_line_key_file(bug_id, dir_path, buggy_line_key_txt, root_dest_dir):
    buggy_line_key_per_bug_version_dir = root_dest_dir / "buggy_line_key_per_bug_version"
    if not buggy_line_key_per_bug_version_dir.exists():
        buggy_line_key_per_bug_version_dir.mkdir(parents=True, exist_ok=True)
    
    dest_file = buggy_line_key_per_bug_version_dir / f"{bug_id}.buggy_line_key.txt"
    sp.check_call(f"cp {buggy_line_key_txt} {dest_file}", shell=True)

def copy_postprocessed_coverage_file(bug_id, dir_path, postprocessed_cov_file, root_dest_dir):
    postprocessed_coverage_per_bug_version_dir = root_dest_dir / "postprocessed_coverage_per_bug_version"
    if not postprocessed_coverage_per_bug_version_dir.exists():
        postprocessed_coverage_per_bug_version_dir.mkdir(parents=True, exist_ok=True)
    
    dest_file = postprocessed_coverage_per_bug_version_dir / f"{bug_id}.cov_data.csv"
    sp.check_call(f"cp {postprocessed_cov_file} {dest_file}", shell=True)

def copy_test_case_info(bug_id, testsuite_info_dir, root_dest_dir):
    test_case_info_per_bug_version_dir = root_dest_dir / "test_case_info_per_bug_version"
    if not test_case_info_per_bug_version_dir.exists():
        test_case_info_per_bug_version_dir.mkdir(parents=True, exist_ok=True)
    
    dest_dir = test_case_info_per_bug_version_dir / bug_id
    dest_dir.mkdir(parents=True, exist_ok=True)

    sp.check_call(f"cp -r {testsuite_info_dir}/* {dest_dir}", shell=True)

def get_feature_per_line(feature_file):
    features_per_line = []
    with open(feature_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            features_per_line.append(row)
    return features_per_line

def write_fl_features_to_csv(
    bug_id, FL_features_per_line,
    root_dest_dir, dest_dir_name,
    dest_file_name, fieldnames
):
    dest_dir = root_dest_dir / dest_dir_name
    if not dest_dir.exists():
        dest_dir.mkdir(parents=True, exist_ok=True)
    
    dest_file = dest_dir / f"{bug_id}.{dest_file_name}"
    with open(dest_file, "w") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in FL_features_per_line:
            new_row = {key: row[key] for key in fieldnames}
            writer.writerow(new_row)
                

def combine_sbfl_mbfl_features(bug_id, sbfl_feature_file, mbfl_feature_file, root_dest_dir, mutant_keys):
    sbfl_features_per_line = get_feature_per_line(sbfl_feature_file)
    mbfl_features_per_line = get_feature_per_line(mbfl_feature_file)
    assert len(sbfl_features_per_line) == len(mbfl_features_per_line), "SBFL and MBFL features have different number of lines"

    FL_features_per_line = []

    for sbfl_row, mbfl_row in zip(sbfl_features_per_line, mbfl_features_per_line):
        assert sbfl_row["key"] == mbfl_row["key"], "SBFL and MBFL features have different keys"
        assert sbfl_row["bug"] == mbfl_row["bug"], "SBFL and MBFL features have different bug ids"

        mutant_dict = {mutant_key: mbfl_row[mutant_key] for mutant_key in mutant_keys}

        fl_row = {
            "key": sbfl_row["key"],
            "ep": sbfl_row["ep"],
            "ef": sbfl_row["ef"],
            "np": sbfl_row["np"],
            "nf": sbfl_row["nf"],
            "# of totfailed_TCs": mbfl_row["# of totfailed_TCs"],
            "# of mutants": mbfl_row["# of mutants"],
            **mutant_dict,
            "bug": sbfl_row["bug"],
            met_key: mbfl_row[met_key],
            muse_key: mbfl_row[muse_key]
        }

        FL_features_per_line.append(fl_row)
    
    fieldnames = list(FL_features_per_line[0].keys())
    write_fl_features_to_csv(
        bug_id, FL_features_per_line, root_dest_dir,
        "FL_features_per_bug_version_with_susp_scores", "fl_features_with_susp_scores.csv", fieldnames=fieldnames)
    
    fieldnames.remove(met_key)
    fieldnames.remove(muse_key)
    write_fl_features_to_csv(
        bug_id, FL_features_per_line, root_dest_dir,
        "FL_features_per_bug_version", "fl_features.csv", fieldnames=fieldnames)

def write_bug_version_mutation_info(
        bug_id, target_file_name,
        bug_code_filename, root_dest_dir,
        mutant_info_csv_file, bug_version_mutation_info_fp
    ):

    if not mutant_info_csv_file.exists():
        bug_version_mutation_info_fp.write(
            f"{bug_id},{target_file_name},{bug_code_filename},,,,,,,,,,,,\n"
        )
    else:
        with open(mutant_info_csv_file, "r") as f:
            lines = f.readlines()
            line = lines[2]
            bug_code_filename_from_line = line.split(",")[0]
            assert bug_code_filename == bug_code_filename_from_line, f"Bug code filename from line {line} is different from {bug_code_filename}"
            bug_version_mutation_info_fp.write(
                f"{bug_id},{target_file_name},{line}\n"
            )

def copy_generated_mutants(
    bug_id, zip_file, root_dest_dir, trial # 2024-08-19
):
    generated_mutants_for_mbfl_per_bug = root_dest_dir / "generated_mutants_for_mbfl_per_bug"
    if not generated_mutants_for_mbfl_per_bug.exists():
        generated_mutants_for_mbfl_per_bug.mkdir(parents=True, exist_ok=True)
    
    dest_bug_dir = generated_mutants_for_mbfl_per_bug / bug_id
    dest_bug_dir.mkdir(parents=True, exist_ok=True)

    trial_dir = dest_bug_dir / trial
    sp.check_call(f"unzip -q {zip_file} -d {trial_dir}", shell=True)
