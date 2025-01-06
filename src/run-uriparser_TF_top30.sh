# 1. Collect buggy mutants
# date > ../timer/uriparser_TF_top30/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject uriparser_TF_top30 --experiment-name TF_top30 > ../timer/uriparser_TF_top30/stage01.log
# date > ../timer/uriparser_TF_top30/stage01_end-remote.txt


# Number of tasks (assigned-stage01): 314
# Number of tasks (mutants-stage01): 331
# Number of tasks (repo): 150
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30

# sec: 403.33572793006897
# min: 6.722262132167816
# hour: 0.11203770220279693

# 191 buggy mutants

# ===============================


# 2. Select usable versions
# date > ../timer/uriparser_TF_top30/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject uriparser_TF_top30 --experiment-name TF_top30 > ../timer/uriparser_TF_top30/stage02.log
# date > ../timer/uriparser_TF_top30/stage02_end-remote.txt

# Number of tasks (assigned_works): 150
# Number of tasks (works): 191
# Number of tasks (repo): 150
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30

# sec: 94.52296662330627
# min: 1.5753827770551045
# hour: 0.026256379617585077

# time python3 validator.py --subject jsoncpp --set-name usable_buggy_versions --validate-usable-buggy-versions

# 148 usable buggy versions



# ===============================


# 3. Prepare prerequisites
# date > ../timer/uriparser_TF_top30/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject uriparser_TF_top30 --experiment-name TF_top30 --version-limit 240 > ../timer/uriparser_TF_top30/stage03.log
# date > ../timer/uriparser_TF_top30/stage03_end-remote.txt


# Number of buggy versions: 148
# Number of tasks (assigned_works): 150
# Number of tasks (works): 148
# Number of tasks (repo): 150
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30

# sec: 103.42593336105347
# min: 1.7237655560175578
# hour: 0.028729425933625964

# 148 valid prerequisites


# time python3 validator.py --subject jsoncpp --set-name prerequisite_data --validate-prerequisite-data
# time python3 analyzer.py --subject jsoncpp --set-name prerequisite_data --output-csv prerequisite_data-tc-stats --prerequisite-data --removed-initialization-coverage



# ===============================

# 4. Extract SBFL features

# date > ../timer/uriparser_TF_top30/stage04_start-remote.txt
# time python3 extract_sbfl_features.py --subject uriparser_TF_top30 --experiment-name TF_top30 --target-set-name prerequisite_data > ../timer/uriparser_TF_top30/stage04.log
# date > ../timer/uriparser_TF_top30/stage04_end-remote.txt

# Number of tasks (assigned_works): 150
# Number of tasks (works): 148
# Number of tasks (repo): 150
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30

# sec: 12.723460912704468
# min: 0.2120576818784078
# hour: 0.003534294697973463

# 148 valid SBFL features


# ===============================

# 5. Extract MBFL features

# date > ../timer/uriparser_TF_top30/stage05_start-remote.txt
# time python3 extract_mbfl_features.py --subject uriparser_TF_top30 --experiment-name TF_top30 --target-set-name prerequisite_data --trial trial1 --parallel-cnt 3 --dont-terminate-leftovers --version-limit 240 > ../timer/uriparser_TF_top30/stage05.log
# date > ../timer/uriparser_TF_top30/stage05_end-remote.txt

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


# extracted 148 valid MBFL features
