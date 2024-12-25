# 1. Collect buggy mutants
# date > ../timer/jsoncpp/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject jsoncpp_test --experiment-name test1
# date > ../timer/jsoncpp/stage01_end-remote.txt

# Number of tasks (assigned-stage01): 816
# Number of tasks (mutants-stage01): 9374
# Number of tasks (repo): 272
# Number of tasks (configurations): 34
# Number of tasks (src): 34
# Number of tasks (tools): 34

# 0:15:20

# 4432 buggy mutants


# ===============================


# 2. Select usable versions
# date > ../timer/jsoncpp/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject jsoncpp_test --experiment-name test1
# date > ../timer/jsoncpp/stage02_end-remote.txt

# Number of tasks (assigned_works): 272
# Number of tasks (works): 2000
# Number of tasks (repo): 272
# Number of tasks (configurations): 34
# Number of tasks (src): 34
# Number of tasks (tools): 34
# Number of tasks (configurations): 34

# 0:04:15

# time python3 validator.py --subject jsoncpp --set-name usable_buggy_versions --validate-usable-buggy-versions

# 1179 usable buggy versions



# ===============================


# 3. Prepare prerequisites
# date > ../timer/jsoncpp/stage03_start-remote.txt
time python3 prepare_prerequisites.py --subject jsoncpp_test --experiment-name test1
# date > ../timer/jsoncpp/stage03_end-remote.txt


# Number of tasks (assigned_works): 272
# Number of tasks (works): 1179
# Number of tasks (repo): 272
# Number of tasks (configurations): 34
# Number of tasks (src): 34
# Number of tasks (tools): 34
# Number of tasks (configurations): 34

# real    6m39.909s
# user    1m20.045s
# sys     1m1.440s

# 1148 valid prerequisites


# time python3 validator.py --subject jsoncpp --set-name prerequisite_data --validate-prerequisite-data
# time python3 analyzer.py --subject jsoncpp --set-name prerequisite_data --output-csv prerequisite_data-tc-stats --prerequisite-data --removed-initialization-coverage



# ===============================

time python3 extract_sbfl_features.py --subject jsoncpp_test --experiment-name test1 --target-set-name prerequisite_data


time python3 extract_mbfl_features.py --subject jsoncpp_test --experiment-name test1 --target-set-name prerequisite_data --trial trial1 --parallel-cnt 2
