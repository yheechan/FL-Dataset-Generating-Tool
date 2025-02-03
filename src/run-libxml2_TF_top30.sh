# 1. Collect buggy mutants
# date > ../timer/libxml2_TF_top30/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject libxml2_TF_top30 --experiment-name TF_top30 > ../timer/libxml2_TF_top30/stage01.log
# date > ../timer/libxml2_TF_top30/stage01_end-remote.txt


# Number of tasks (assigned-stage01): 1147
# Number of tasks (mutants-stage01): 7457
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 1219.0450956821442
# min: 20.31741826136907
# hour: 0.3386236376894845

# 1,560 buggy mutants

# ===============================


# 2. Select usable versions
# date > ../timer/libxml2_TF_top30/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject libxml2_TF_top30 --experiment-name TF_top30 > ../timer/libxml2_TF_top30/stage02.log
# date > ../timer/libxml2_TF_top30/stage02_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 1560
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 286.24310517311096
# min: 4.77071841955185
# hour: 0.0795119736591975


# 1374 usable buggy versions



# ===============================


# 3. Prepare prerequisites
# date > ../timer/libxml2_TF_top30/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject libxml2_TF_top30 --experiment-name TF_top30 --version-limit 240 > ../timer/libxml2_TF_top30/stage03.log
# date > ../timer/libxml2_TF_top30/stage03_end-remote.txt


# Number of buggy versions: 1374
# Number of tasks (assigned_works): 232
# Number of tasks (works): 240
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 288.6073019504547
# min: 4.810121699174245
# hour: 0.08016869498623742

# 237 valid prerequisites


# python3 validator.py --subject libxml2_TF_top30 --experiment-name TF_top30 --validation-criteria 1,2,3,4,5,6



# ===============================

# 4. Extract SBFL features

# date > ../timer/libxml2_TF_top30/stage04_start-remote.txt
# time python3 extract_sbfl_features.py --subject libxml2_TF_top30 --experiment-name TF_top30 --target-set-name prerequisite_data > ../timer/libxml2_TF_top30/stage04.log
# date > ../timer/libxml2_TF_top30/stage04_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 237
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 91.02879452705383
# min: 1.5171465754508973
# hour: 0.025285776257514953

# 237 valid SBFL features

# python3 validator.py --subject libxml2_TF_top30 --experiment-name TF_top30 --validation-criteria 7
# python3 analyzer.py --subject libxml2_TF_top30 --experiment-name TF_top30 --analysis-criteria 1

# ===============================

# 5. Extract MBFL features

# date > ../timer/libxml2_TF_top30/stage05_start-remote.txt
# time python3 extract_mbfl_features.py --subject libxml2_TF_top30 --experiment-name TF_top30 --target-set-name prerequisite_data --trial trial1 --parallel-cnt 3 --dont-terminate-leftovers --remain-one-bug-per-line --version-limit 240 > ../timer/libxml2_TF_top30/stage05.log
# date > ../timer/libxml2_TF_top30/stage05_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 236
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 104225.63932728767
# min: 1737.093988788128
# hour: 28.951566479802132

# extracted 240 valid MBFL features

# python3 validator.py --subject libxml2_TF_top30 --experiment-name TF_top30 --validation-criteria 8,9,10
# python3 analyzer.py --subject libxml2_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject libxml2_TF_top30 --experiment-name TF_top30 --analysis-criteria 4