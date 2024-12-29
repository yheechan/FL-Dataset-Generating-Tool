from pathlib import Path
import time
import json
import csv

# src/lib/utils.py
root_dir = Path(__file__).resolve().parent.parent.parent

work_dir = root_dir / "work"
work_dir.mkdir(exist_ok=True)
log_dir = root_dir / "log"
log_dir.mkdir(exist_ok=True)
out_dir = root_dir / "out"
out_dir.mkdir(exist_ok=True)
stats_dir = root_dir / "statistics"
stats_dir.mkdir(exist_ok=True)

configs_dir = root_dir / "configs"
subjects_dir = root_dir / "subjects"
tools_dir = root_dir / "tools"
src_dir = root_dir / "src"

# files in user_configs_dir
configure_no_cov_script = 'configure_no_cov_script.sh'
configure_yes_cov_script = 'configure_yes_cov_script.sh'
build_script = 'build_script.sh'
clean_script = 'clean_script.sh'
machines_json_file = 'machines.json'
configure_json_file = 'configurations.json'

# Not using operators when collecting buggy mutants
not_using_operators_in_buggy_mutant_collection = [
    "DirVarAriNeg", "DirVarBitNeg", "DirVarLogNeg", "DirVarIncDec",
    "DirVarRepReq", "DirVarRepCon", "DirVarRepPar", "DirVarRepGlo", 
    "DirVarRepExt", "DirVarRepLoc", "IndVarAriNeg", "IndVarBitNeg", 
    "IndVarLogNeg", "IndVarIncDec", "IndVarRepReq", "IndVarRepCon", 
    "IndVarRepPar", "IndVarRepGlo", "IndVarRepExt", "IndVarRepLoc",
    "SSDL", "CovAllNod", "CovAllEdg", "STRP", "STRI", "VDTR",
    "RetStaDel", "FunCalDel", "SMVB",
    "SMTC" # This makes music to see buggy line as line at "{"
]

not_using_operators_in_mbfl = [
    "DirVarAriNeg", "DirVarBitNeg", "DirVarLogNeg", "DirVarIncDec",
    "DirVarRepReq", "DirVarRepCon", "DirVarRepPar", "DirVarRepGlo", 
    "DirVarRepExt", "DirVarRepLoc", "IndVarAriNeg", "IndVarBitNeg", 
    "IndVarLogNeg", "IndVarIncDec", "IndVarRepReq", "IndVarRepCon", 
    "IndVarRepPar", "IndVarRepGlo", "IndVarRepExt", "IndVarRepLoc",
    "STRI"
]

crash_codes = [
    132,  # SIGILL
    133,  # SIGTRAP
    134,  # SIGABRT
    135,  # SIGBUS
    136,  # SIGFPE
    137,  # SIGKILL
    138,  # SIGBUS
    139,  # segfault
    140,  # SIGPIPE
    141,  # SIGALRM
    124,  # timeout
    143,  # SIGTERM
    129,  # SIGHUP
]

crash_codes_dict = {
    132: "SIGILL",
    133: "SIGTRAP",
    134: "SIGABRT",
    135: "SIGBUS",
    136: "SIGFPE",
    137: "SIGKILL",
    138: "SIGBUS",
    139: "segfault",
    140: "SIGPIPE",
    141: "SIGALRM",
    124: "timeout",
    143: "SIGTERM",
    129: "SIGHUP"
}

def sort_testcase_script_name(tc_script):
    tc_filename = tc_script.split('.')[0]
    return int(tc_filename[2:])

def sort_bug_id(bug_id):
    return int(bug_id[3:])

def get_dirs_in_dir(directory):
    return [d for d in directory.iterdir() if d.is_dir()]
def get_files_in_dir(directory):
    return [f for f in directory.iterdir() if not f.is_dir()]

def print_command(command, verbose):
    # print command if verbose is true (with data and time)
    if verbose:
        command = [str(c) for c in command]
        command = " ".join(command)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {command}")

def get_tc_list(tc_file):
        if not tc_file.exists():
            return []
        
        tc_list = []
        with open(tc_file, "r") as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line != "":
                    tc_list.append(line)
        
        tc_list = sorted(tc_list, key=sort_testcase_script_name)
        return tc_list

def measure_MBFL_feature_value(row, mutant_keys, f2p_or_p2f):
    feature_value = 0

    for key in mutant_keys:
        if f2p_or_p2f in key and int(row[key]) != -1:
            feature_value += int(row[key])

    return feature_value

def analyze_buggy_line_with_f2p_0(mbfl_features_csv_file, buggy_line_key, mutant_keys):
        target_buggy_file = buggy_line_key.split('#')[0].split('/')[-1]
        buggy_function_name = buggy_line_key.split('#')[1]
        buggy_lineno = int(buggy_line_key.split('#')[-1])

        good_mutants = []

        with open(mbfl_features_csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = row['key']
                current_target_file = key.split('#')[0].split('/')[-1]
                current_function_name = key.split('#')[1]
                current_lineno = int(key.split('#')[-1])

                if current_target_file == target_buggy_file and \
                    current_function_name == buggy_function_name:

                    feature_value = measure_MBFL_feature_value(row, mutant_keys, 'f2p')
                    if feature_value != 0:
                        good_mutants.append(row)
        
        if len(good_mutants) == 0:
            return 0
        
        return 1

def avg_killed(row, mutant_keys, f2p_or_p2f):
    # returns 0 if there is no f2p or p2f in the row
    # returns the average of f2p or p2f scores if there is f2p or p2f in the row
    f2p_scores = []
    for key in mutant_keys:
        if f2p_or_p2f in key and int(row[key]) != -1:
            f2p_scores.append(int(row[key]))

    if len(f2p_scores) == 0:
        return 0
    avg_score = sum(f2p_scores) / len(f2p_scores)

    return avg_score

def analyze_non_buggy_line_with_f2p_above_th(
        mbfl_features_csv_file, buggy_line_key, mutant_keys, threshold
):
    target_buggy_file = buggy_line_key.split('#')[0].split('/')[-1]
    buggy_function_name = buggy_line_key.split('#')[1]
    buggy_lineno = int(buggy_line_key.split('#')[-1])

    bad_line = []

    with open(mbfl_features_csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row['key']
            current_target_file = key.split('#')[0].split('/')[-1]
            current_function_name = key.split('#')[1]
            current_lineno = int(key.split('#')[-1])

            num_mutants = int(row['|muse(s)|'])

            num_failing_tcs_at_line = int(row['#_failing_tcs_@line'])
            perc50 = num_failing_tcs_at_line / 2

            if current_target_file != target_buggy_file or \
                current_function_name != buggy_function_name or \
                    current_lineno != buggy_lineno:

                # mutant list which its mutants have f2p == fail_cnt
                avg_f2p_score = avg_killed(row, mutant_keys, 'f2p')

                # if average f2p of a line is greater than 50% of the failing TCs at the line
                if avg_f2p_score > perc50:
                    bad_line.append(row)
    
    # if # of bad lines is greater than threshold
    # then return 0
    if len(bad_line) > threshold:
        return 0
    
    # if # of bad lines is less than or equal to threshold
    # then return 1
    return 1
    
def get_lines_executed_by_failing_tcs_from_data(version_dir):
    get_lines_executed_by_failing_tcs_file = version_dir / "coverage_info/lines_executed_by_failing_tc.json"
    assert get_lines_executed_by_failing_tcs_file.exists(), f"lines_executed_by_failing_tc.json does not exist in {version_dir}"

    with open(get_lines_executed_by_failing_tcs_file, "r") as f:
        lines_executed_by_failing_tcs = json.load(f)
    
    return lines_executed_by_failing_tcs

def get_lines_executed_on_initialization(version_dir): # 2024-08-13 exclude lines executed on initialization
    get_lines_executed_by_failing_tcs_file = version_dir / "coverage_info/lines_executed_at_initialization.txt"
    assert get_lines_executed_by_failing_tcs_file.exists(), f"lines_executed_at_initialization.txt does not exist in {version_dir}"

    with open(get_lines_executed_by_failing_tcs_file, "r") as f:
        lines = f.readlines()
        lines = [line.strip() for line in lines]
    
    return lines

def get_linse_exected_on_initialization_as_filenm2lineno(version_dir): # 2024-08-13 exclude lines executed on initialization
    get_lines_executed_by_failing_tcs_file = version_dir / "coverage_info/lines_executed_at_initialization.txt"
    assert get_lines_executed_by_failing_tcs_file.exists(), f"lines_executed_at_initialization.txt does not exist in {version_dir}"

    with open(get_lines_executed_by_failing_tcs_file, "r") as f:
        lines = f.readlines()
        filenm2lineno = {}
        for line in lines:
            info = line.strip().split("#")
            filenm = info[0].split("/")[-1]
            func = info[1]
            lineno = info[-1]
            if filenm not in filenm2lineno:
                filenm2lineno[filenm] = []
            filenm2lineno[filenm].append(lineno)
    
    return filenm2lineno

def get_postprocessed_coverage_csv_file_from_data(version_dir):
    pp_cov_csv_file = version_dir / "coverage_info/postprocessed_coverage.csv"
    assert pp_cov_csv_file.exists(), f"{pp_cov_csv_file} doesn't exists"

    lines = []
    with open(pp_cov_csv_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lines.append(row)
    
    return lines

def get_buggy_line_key_from_data(version_dir):
    buggy_line_key_file = version_dir / "buggy_line_key.txt"
    assert buggy_line_key_file.exists(), f"buggy_line_key.txt does not exist in {version_dir}"
    
    with open(buggy_line_key_file, "r") as f:
        buggy_line_key = f.readline().strip()
    
    return buggy_line_key

def get_file_func_pair_executed_by_failing_tcs(lines_executed_by_failing_tcs):
    funcs_executed_by_failing_tcs = []
    for key in lines_executed_by_failing_tcs:
        file_name = key.split('#')[0]
        func_name = key.split('#')[1]
        if (file_name, func_name) not in funcs_executed_by_failing_tcs:
            funcs_executed_by_failing_tcs.append((file_name, func_name))
    return funcs_executed_by_failing_tcs

def divide_list(lst, n):
    k, m = divmod(len(lst), n)
    return [lst[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)]


def get_mutation_testing_results_csv_row(csv_file):
    mutant_list = []
    with open(csv_file, "r") as fp:
        lines = fp.readlines()
        for line in lines[1:]:
            line = line.strip()
            mutant_list.append(line)
    return mutant_list

def list_of_ints(arg):
    return list(map(int, arg.split(',')))