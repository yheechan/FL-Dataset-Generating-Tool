# 1. Collect buggy mutants
# date > ../timer/zlib_ng_TF_bot30/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 > ../timer/zlib_ng_TF_bot30/stage01.log
# date > ../timer/zlib_ng_TF_bot30/stage01_end-remote.txt


# Number of tasks (assigned-stage01): 1596
# Number of tasks (mutants-stage01): 4771
# Number of tasks (repo): 240
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30

# sec: 900.2728626728058
# min: 15.00454771121343
# hour: 0.2500757951868905

# 1009 buggy mutants

# ===============================


# 2. Select usable versions
# date > ../timer/zlib_ng_TF_bot30/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 > ../timer/zlib_ng_TF_bot30/stage02.log
# date > ../timer/zlib_ng_TF_bot30/stage02_end-remote.txt

# Number of tasks (assigned_works): 240
# Number of tasks (works): 1009
# Number of tasks (repo): 240
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30

# sec: 186.34420037269592
# min: 3.1057366728782654
# hour: 0.05176227788130442

# 648 usable buggy versions



# ===============================


# 3. Prepare prerequisites
# date > ../timer/zlib_ng_TF_bot30/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 > ../timer/zlib_ng_TF_bot30/stage03.log
# date > ../timer/zlib_ng_TF_bot30/stage03_end-remote.txt


# Number of buggy versions: 648
# Number of tasks (assigned_works): 240
# Number of tasks (works): 648
# Number of tasks (repo): 240
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30

# sec: 471.83219623565674
# min: 7.8638699372609455
# hour: 0.1310644989543491

# 648 valid prerequisites


# ===============================

# 4. Extract SBFL features

# date > ../timer/zlib_ng_TF_bot30/stage04_start-remote.txt
# time python3 extract_sbfl_features.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --target-set-name prerequisite_data > ../timer/zlib_ng_TF_bot30/stage04.log
# date > ../timer/zlib_ng_TF_bot30/stage04_end-remote.txt

# Number of tasks (assigned_works): 240
# Number of tasks (works): 648
# Number of tasks (repo): 240
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30

# sec: 30.50662899017334
# min: 0.508443816502889
# hour: 0.008474063608381483

# 648 valid SBFL features

# python3 validator.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --validation-criteria 1,2,3,4,5,6,7


# ===============================

# 5. Extract MBFL features

date > ../timer/zlib_ng_TF_bot30/stage05_start-remote.txt
time python3 extract_mbfl_features.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --target-set-name prerequisite_data --trial trial1 --parallel-cnt 3 --dont-terminate-leftovers --version-limit 240 --remain-one-bug-per-line > ../timer/zlib_ng_TF_bot30/stage05.log
date > ../timer/zlib_ng_TF_bot30/stage05_end-remote.txt


# Number of tasks (assigned_works): 240
# Number of tasks (works): 180
# Number of tasks (repo): 240
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30

# sec: 12556.776431798935
# min: 209.27960719664893
# hour: 3.487993453277482


# extracted 180 valid MBFL features


# python3 validator.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --validation-criteria 0
# python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 1
# python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name 
