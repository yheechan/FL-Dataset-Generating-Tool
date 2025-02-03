# 1. Collect buggy mutants
# date > ../timer/opencv_calib3d_TF_top30/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject opencv_calib3d_TF_top30 --experiment-name TF_top30 > ../timer/opencv_calib3d_TF_top30/stage01.log
# date > ../timer/opencv_calib3d_TF_top30/stage01_end-remote.txt


# Number of tasks (assigned-stage01): 2194
# Number of tasks (mutants-stage01): 4446
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 5386.863002300262
# min: 89.78105003833771
# hour: 1.496350833972295

# 1408 buggy mutants

# ===============================


# 2. Select usable versions
# date > ../timer/opencv_calib3d_TF_top30/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject opencv_calib3d_TF_top30 --experiment-name TF_top30 > ../timer/opencv_calib3d_TF_top30/stage02.log
# date > ../timer/opencv_calib3d_TF_top30/stage02_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 1408
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 1500.5978543758392
# min: 25.00996423959732
# hour: 0.416832737326622


# 1050 usable buggy versions



# ===============================


# 3. Prepare prerequisites
# date > ../timer/opencv_calib3d_TF_top30/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject opencv_calib3d_TF_top30 --experiment-name TF_top30 --version-limit 464 > ../timer/opencv_calib3d_TF_top30/stage03.log
# date > ../timer/opencv_calib3d_TF_top30/stage03_end-remote.txt


# Number of buggy versions: 1050
# Number of tasks (assigned_works): 232
# Number of tasks (works): 464
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29


# sec: 1941.8882088661194
# min: 32.36480348110199
# hour: 0.5394133913516997

# 464 valid prerequisites


# python3 validator.py --subject opencv_calib3d_TF_top30 --experiment-name TF_top30 --validation-criteria 1,2,3,4,5,6



# ===============================

# 4. Extract SBFL features

# date > ../timer/opencv_calib3d_TF_top30/stage04_start-remote.txt
# time python3 extract_sbfl_features.py --subject opencv_calib3d_TF_top30 --experiment-name TF_top30 --target-set-name prerequisite_data > ../timer/opencv_calib3d_TF_top30/stage04.log
# date > ../timer/opencv_calib3d_TF_top30/stage04_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 464
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 157.32765126228333
# min: 2.6221275210380552
# hour: 0.04370212535063425

# 464 valid SBFL features

# python3 validator.py --subject opencv_calib3d_TF_top30 --experiment-name TF_top30 --validation-criteria 7
# python3 analyzer.py --subject opencv_calib3d_TF_top30 --experiment-name TF_top30 --analysis-criteria 1

# ===============================

# 5. Extract MBFL features

# date > ../timer/opencv_calib3d_TF_top30/stage05_start-remote.txt
# time python3 extract_mbfl_features.py --subject opencv_calib3d_TF_top30 --experiment-name TF_top30 --target-set-name prerequisite_data --trial trial1 --parallel-cnt 3 --dont-terminate-leftovers --remain-one-bug-per-line --version-limit 232 > ../timer/opencv_calib3d_TF_top30/stage05.log
# date > ../timer/opencv_calib3d_TF_top30/stage05_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 232
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 162349.67568945885
# min: 2705.8279281576474
# hour: 45.09713213596079

# extracted 231 valid MBFL features

# python3 validator.py --subject opencv_calib3d_TF_top30 --experiment-name TF_top30 --validation-criteria 8,9,10
# python3 analyzer.py --subject opencv_calib3d_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject opencv_calib3d_TF_top30 --experiment-name TF_top30 --analysis-criteria 4