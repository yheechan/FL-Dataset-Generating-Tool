from pathlib import Path

# src/lib/utils.py
root_dir = Path(__file__).resolve().parent.parent.parent
work_dir = root_dir / "work"
work_dir.mkdir(exist_ok=True)
configs_dir = root_dir / "configs"
subjects_dir = root_dir / "subjects"
tools_dir = root_dir / "tools"
log_dir = root_dir / "logs"

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