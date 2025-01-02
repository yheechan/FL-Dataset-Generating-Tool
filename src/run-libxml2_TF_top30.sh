# 1. Collect buggy mutants
# date > ../timer/libxml2_TF_top30/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject libxml2_TF_top30 --experiment-name TF_top30 > ../timer/libxml2_TF_top30/stage01.log
#  date > ../timer/libxml2_TF_top30/stage01_end-remote.txt


# Number of tasks (assigned-stage01): 2400
# Number of tasks (mutants-stage01): 53401
# Number of tasks (repo): 240
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30

# sec: 12498.899003505707
# min: 208.31498339176179
# hour: 3.4719163898626966

# 17,033 buggy mutants

# ===============================


# 2. Select usable versions
# date > ../timer/libxml2_TF_top30/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject libxml2_TF_top30 --experiment-name TF_top30 > ../timer/libxml2_TF_top30/stage02.log
# date > ../timer/libxml2_TF_top30/stage02_end-remote.txt

# Number of tasks (assigned_works): 240
# Number of tasks (works): 2000
# Number of tasks (repo): 240
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30

# sec: ?
# min: ?
# hour: ?

# time python3 validator.py --subject jsoncpp --set-name usable_buggy_versions --validate-usable-buggy-versions

# 1694 usable buggy versions



# ===============================


# 3. Prepare prerequisites
date > ../timer/libxml2_TF_top30/stage03_start-remote.txt
time python3 prepare_prerequisites.py --subject libxml2_TF_top30 --experiment-name TF_top30 > ../timer/libxml2_TF_top30/stage03.log
date > ../timer/libxml2_TF_top30/stage03_end-remote.txt


# Number of tasks (assigned_works): 128
# Number of tasks (works): 1225
# Number of tasks (repo): 128
# Number of tasks (configurations): 16
# Number of tasks (src): 16
# Number of tasks (tools): 16
# Number of tasks (configurations): 16

# sec: 3268.8114070892334
# min: 54.48019011815389
# hour: 0.9080031686358983

# 1223 valid prerequisites


# time python3 validator.py --subject jsoncpp --set-name prerequisite_data --validate-prerequisite-data
# time python3 analyzer.py --subject jsoncpp --set-name prerequisite_data --output-csv prerequisite_data-tc-stats --prerequisite-data --removed-initialization-coverage



# ===============================

# 4. Extract SBFL features

# date > ../timer/libxml2_TF_top30/stage04_start-remote.txt
# time python3 extract_sbfl_features.py --subject libxml2_TF_top30 --experiment-name TF_top30 --target-set-name prerequisite_data > ../timer/libxml2_TF_top30/stage04.log
# date > ../timer/libxml2_TF_top30/stage04_end-remote.txt

# Number of tasks (assigned_works): 128
# Number of tasks (works): 1223
# Number of tasks (repo): 128
# Number of tasks (configurations): 16
# Number of tasks (src): 16
# Number of tasks (tools): 16
# Number of tasks (configurations): 16

# sec: 338.69401955604553
# min: 5.644900325934092
# hour: 0.09408167209890153

# 1223 valid SBFL features


# ===============================

# 5. Extract MBFL features

# date > ../timer/libxml2_TF_top30/stage05_start-remote.txt
# time python3 extract_mbfl_features.py --subject libxml2_TF_top30 --experiment-name TF_top30 --target-set-name prerequisite_data --trial trial1 --parallel-cnt 3 --dont-terminate-leftovers --remain-one-bug-per-line --version-limit 240 > ../timer/libxml2_TF_top30/stage05.log
# date > ../timer/libxml2_TF_top30/stage05_end-remote.txt

# sec: 244.33251810073853
# min: 4.072208635012308
# hour: 0.06787014391687181

# Number of tasks (assigned_works): 240
# Number of tasks (works): 671
# Number of tasks (repo): 240
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30


# extracted 240 valid MBFL features
