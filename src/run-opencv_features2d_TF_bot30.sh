# 1. Collect buggy mutants
# date > ../timer/opencv_features2d_TF_bot30/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 > ../timer/opencv_features2d_TF_bot30/stage01.log
# date > ../timer/opencv_features2d_TF_bot30/stage01_end-remote.txt

# Number of tasks (assigned-stage01): 1307
# Number of tasks (mutants-stage01): 2432
# Number of tasks (repo): 240
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30


# sec: 4080.9763453006744
# min: 68.01627242167791
# hour: 1.1336045403612984

# 461 buggy mutants

# ===============================


# 2. Select usable versions
# date > ../timer/opencv_features2d_TF_bot30/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 > ../timer/opencv_features2d_TF_bot30/stage02.log
# date > ../timer/opencv_features2d_TF_bot30/stage02_end-remote.txt

# Number of tasks (assigned_works): 240
# Number of tasks (works): 461
# Number of tasks (repo): 240
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30

# sec: 2688.623957157135
# min: 44.81039928595225
# hour: 0.7468399880992042

# time python3 validator.py --subject jsoncpp --set-name usable_buggy_versions --validate-usable-buggy-versions

# 359 usable buggy versions



# ===============================


# 3. Prepare prerequisites
# date > ../timer/opencv_features2d_TF_bot30/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 > ../timer/opencv_features2d_TF_bot30/stage03.log
# date > ../timer/opencv_features2d_TF_bot30/stage03_end-remote.txt


# Number of tasks (assigned_works): 240
# Number of tasks (works): 359
# Number of tasks (repo): 240
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30

# real    6m39.909s
# user    1m20.045s
# sys     1m1.440s

# 357 valid prerequisites


# time python3 validator.py --subject jsoncpp --set-name prerequisite_data --validate-prerequisite-data
# time python3 analyzer.py --subject jsoncpp --set-name prerequisite_data --output-csv prerequisite_data-tc-stats --prerequisite-data --removed-initialization-coverage



# ===============================

# date > ../timer/opencv_features2d_TF_bot30/stage04_start-remote.txt
# time python3 extract_sbfl_features.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --target-set-name prerequisite_data
# date > ../timer/opencv_features2d_TF_bot30/stage04_end-remote.txt

# Number of tasks (assigned_works): 240
# Number of tasks (works): 357
# Number of tasks (repo): 240
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30

# sec: 79.06742668151855
# min: 1.317790444691976
# hour: 0.021963174078199598

# 357 valid sbfl features



# ===============================


# 5. Extract MBFL features
# date > ../timer/opencv_features2d_TF_bot30/stage05_start-remote.txt
# time python3 extract_mbfl_features.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --target-set-name prerequisite_data --trial trial1 --parallel-cnt 3 --dont-terminate-leftovers --remain-one-bug-per-line > ../timer/opencv_features2d_TF_bot30/stage05.log
# date > ../timer/opencv_features2d_TF_bot30/stage05_end-remote.txt


# Number of tasks (assigned_works): 120
# Number of tasks (works): 120
# Number of tasks (repo): 120
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30


# sec: 10944.735776901245
# min: 182.41226294835408
# hour: 3.040204382472568

