# 1. Collect buggy mutants
# date > ../timer/opencv_core_exp1/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject opencv_core_exp1 --experiment-name e1 > ../timer/opencv_core_exp1/stage01.log
# date > ../timer/opencv_core_exp1/stage01_end-remote.txt


# Number of tasks (assigned-stage01): 1639
# Number of tasks (mutants-stage01): 3311
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 5171.350893735886
# min: 86.18918156226476
# hour: 1.4364863593710795

# 910 buggy mutants

# ===============================


# 2. Select usable versions
# date > ../timer/opencv_core_exp1/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject opencv_core_exp1 --experiment-name e1 > ../timer/opencv_core_exp1/stage02.log
# date > ../timer/opencv_core_exp1/stage02_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 910
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 1517.433001756668
# min: 25.290550029277803
# hour: 0.42150916715463005


# 618 usable buggy versions



# ===============================


# 3. Prepare prerequisites
# date > ../timer/opencv_core_exp1/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject opencv_core_exp1 --experiment-name e1 --version-limit 618 > ../timer/opencv_core_exp1/stage03.log
# date > ../timer/opencv_core_exp1/stage03_end-remote.txt


# Number of buggy versions: 618
# Number of tasks (assigned_works): 232
# Number of tasks (works): 618
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29


# sec: 2305.7676033973694
# min: 38.42946005662282
# hour: 0.6404910009437137

# 605 valid prerequisites


# python3 validator.py --subject libxml2_exp1 --experiment-name e1 --validation-criteria 1,2,3,4,5,6,7



# ===============================

# 4. Extract SBFL features

# date > ../timer/opencv_core_exp1/stage04_start-remote.txt
# time python3 extract_sbfl_features.py --subject opencv_core_exp1 --experiment-name e1 --target-set-name prerequisite_data > ../timer/opencv_core_exp1/stage04.log
# date > ../timer/opencv_core_exp1/stage04_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 605
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 154.55505752563477
# min: 2.575917625427246
# hour: 0.042931960423787434

# 605 valid SBFL features

# python3 validator.py --subject libxml2_exp1 --experiment-name e1 --validation-criteria 8
# python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 1

# ===============================

# 5. Extract MBFL features

date > ../timer/opencv_core_exp1/stage05_start-remote.txt
time python3 extract_mbfl_features.py --subject opencv_core_exp1 --experiment-name e1 --target-set-name prerequisite_data --trial trial1 --parallel-cnt 8 --dont-terminate-leftovers --remain-one-bug-per-line --version-limit 1 > ../timer/opencv_core_exp1/stage05.log
date > ../timer/opencv_core_exp1/stage05_end-remote.txt

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

# python3 validator.py --subject libxml2_exp1 --experiment-name e1 --validation-criteria 9,10,11,12
# python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 1
# python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 4



# =============================== 50%
# echo "analyzing opencv_core_exp1 allfails-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_core_exp1 --experiment-name e1 --analysis-criteria 2 --type-name allfails-noReduced-excludeCCT-noHeuristics

# echo "analyzing opencv_core_exp1 rand50-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_core_exp1 --experiment-name e1 --analysis-criteria 2 --type-name rand50-noReduced-excludeCCT-noHeuristics

# =============================== 30%

# echo "analyzing opencv_core_exp1 rand30-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_core_exp1 --experiment-name e1 --analysis-criteria 2 --type-name rand30-noReduced-excludeCCT-noHeuristics

# echo "analyzing opencv_core_exp1 sbflnaish230-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_core_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-noReduced-excludeCCT-noHeuristics


# ===============================

# echo "analyzing opencv_core_exp1 sbflnaish250-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_core_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-noReduced-excludeCCT-noHeuristics

# echo "analyzing opencv_core_exp1 sbflnaish250-reduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_core_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-reduced-excludeCCT-noHeuristics

# echo "analyzing opencv_core_exp1 sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_core_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics


# =============================== 30%

# echo "analyzing opencv_core_exp1 sbflnaish230-reduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_core_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-reduced-excludeCCT-noHeuristics

# echo "analyzing opencv_core_exp1 sbflnaish230-reduced_sbflnaish2-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_core_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-reduced_sbflnaish2-excludeCCT-noHeuristics



# ===============================

# time python3 analyzer.py \
#     --subject opencv_core_exp1 \
#     --experiment-name e1 \
#     --analysis-criteria 9 \
#     --batch-size 512

# time python3 analyzer.py \
#     --subject opencv_core_exp1 \
#     --experiment-name e1 \
#     --analysis-criteria 8

# time python3 analyzer.py \
#     --subject opencv_core_exp1 \
#     --experiment-name e1 \
#     --analysis-criteria 9 \
#     --batch-size 512