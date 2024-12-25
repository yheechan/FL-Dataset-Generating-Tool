# 1. Collect buggy mutants
date > ../timer/opencv_features2d_TF_top30/stage01_start-remote.txt
time python3 collect_buggy_mutants.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30
date > ../timer/opencv_features2d_TF_top30/stage01_end-remote.txt

# Number of tasks (assigned-stage01): 768
# Number of tasks (mutants-stage01): 6453
# Number of tasks (repo): 128
# Number of tasks (configurations): 16
# Number of tasks (src): 16
# Number of tasks (tools): 16
# Number of tasks (configurations): 16

# real    73m53.259s
# user    23m53.303s
# sys     5m41.636s

# 1897 buggy mutants

# ===============================


# 2. Select usable versions
# date > ../timer/opencv_features2d_TF_top30/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 > ../timer/opencv_features2d_TF_top30/stage02.log
# date > ../timer/opencv_features2d_TF_top30/stage02_end-remote.txt

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
# date > ../timer/opencv_features2d_TF_top30/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30
# date > ../timer/opencv_features2d_TF_top30/stage03_end-remote.txt


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

# time python3 extract_sbfl_features.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --target-set-name prerequisite_data



# ===============================

# time extract_mbfl_features.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --target-set-name prerequisite_data --trial trial1 --parallel-cnt 2