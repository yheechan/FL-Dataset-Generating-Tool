# 1. Collect buggy mutants
# date > ../timer/opencv_core_TF_top30/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject opencv_core_TF_top30 --experiment-name TF_top30 > ../timer/opencv_core_TF_top30/stage01.log
# date > ../timer/opencv_core_TF_top30/stage01_end-remote.txt


# Number of tasks (assigned-stage01): 2210
# Number of tasks (mutants-stage01): 14314
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 6590.102495670319
# min: 109.83504159450531
# hour: 1.8305840265750886

# 4067 buggy mutants

# ===============================


# 2. Select usable versions
# date > ../timer/opencv_core_TF_top30/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject opencv_core_TF_top30 --experiment-name TF_top30 > ../timer/opencv_core_TF_top30/stage02.log
# date > ../timer/opencv_core_TF_top30/stage02_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 2000
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 1791.1242990493774
# min: 29.852071650822957
# hour: 0.49753452751371596


# 1499 usable buggy versions



# ===============================


# 3. Prepare prerequisites
# date > ../timer/opencv_core_TF_top30/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --version-limit 464 > ../timer/opencv_core_TF_top30/stage03.log
# date > ../timer/opencv_core_TF_top30/stage03_end-remote.txt


# Number of buggy versions: 1499
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

# 455 valid prerequisites


# python3 validator.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --validation-criteria 1,2,3,4,5,6



# ===============================

# 4. Extract SBFL features

# date > ../timer/opencv_core_TF_top30/stage04_start-remote.txt
# time python3 extract_sbfl_features.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --target-set-name prerequisite_data > ../timer/opencv_core_TF_top30/stage04.log
# date > ../timer/opencv_core_TF_top30/stage04_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 455
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 152.22175359725952
# min: 2.537029226620992
# hour: 0.0422838204436832

# 455 valid SBFL features

# python3 validator.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --validation-criteria 7
# python3 analyzer.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --analysis-criteria 1

# ===============================

# 5. Extract MBFL features

# date > ../timer/opencv_core_TF_top30/stage05_start-remote.txt
# time python3 extract_mbfl_features.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --target-set-name prerequisite_data --trial trial1 --parallel-cnt 3 --dont-terminate-leftovers --remain-one-bug-per-line --version-limit 232 > ../timer/opencv_core_TF_top30/stage05.log
# date > ../timer/opencv_core_TF_top30/stage05_end-remote.txt

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

# extracted 232 valid MBFL features

# python3 validator.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --validation-criteria 8,9,10
# python3 analyzer.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --analysis-criteria 4



# =============================== 50%
# echo "analyzing opencv_core_TF_top30 allfails-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name allfails-noReduced-excludeCCT-noHeuristics

# echo "analyzing opencv_core_TF_top30 rand50-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name rand50-noReduced-excludeCCT-noHeuristics

# =============================== 30%

# echo "analyzing opencv_core_TF_top30 rand30-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name rand30-noReduced-excludeCCT-noHeuristics

# echo "analyzing opencv_core_TF_top30 sbflnaish230-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish230-noReduced-excludeCCT-noHeuristics


# ===============================

# echo "analyzing opencv_core_TF_top30 sbflnaish250-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish250-noReduced-excludeCCT-noHeuristics

# echo "analyzing opencv_core_TF_top30 sbflnaish250-reduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish250-reduced-excludeCCT-noHeuristics

# echo "analyzing opencv_core_TF_top30 sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics


# ===============================

time python3 analyzer.py \
    --subject opencv_core_TF_top30 \
    --experiment-name TF_top30 \
    --analysis-criteria 9 \
    --batch-size 512

# time python3 analyzer.py \
#     --subject opencv_core_TF_top30 \
#     --experiment-name TF_top30 \
#     --analysis-criteria 8

# time python3 analyzer.py \
#     --subject opencv_core_TF_top30 \
#     --experiment-name TF_top30 \
#     --analysis-criteria 9 \
#     --batch-size 512