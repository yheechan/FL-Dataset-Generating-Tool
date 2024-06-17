from pathlib import Path
import time

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
    "RetStaDel", "FunCalDel"
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

def sort_testcase_script_name(tc_script):
    tc_filename = tc_script.split('.')[0]
    return int(tc_filename[2:])

def get_dirs_in_dir(directory):
    return [d for d in directory.iterdir() if d.is_dir()]

def print_command(command, verbose):
    # print command if verbose is true (with data and time)
    if verbose:
        command = [str(c) for c in command]
        command = " ".join(command)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {command}")