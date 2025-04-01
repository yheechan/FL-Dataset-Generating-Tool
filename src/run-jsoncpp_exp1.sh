# 1. Collect buggy mutants
# date > ../timer/jsoncpp_exp1/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject jsoncpp_exp1 --experiment-name e1 > ../timer/jsoncpp_exp1/stage01.log
# date > ../timer/jsoncpp_exp1/stage01_end-remote.txt


# Number of tasks (assigned-stage01): 696
# Number of tasks (mutants-stage01): 2159
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 650.5083141326904
# min: 10.841805235544841
# hour: 0.18069675392574736

# 1077 buggy mutants

# ===============================


# 2. Select usable versions
# date > ../timer/jsoncpp_exp1/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject jsoncpp_exp1 --experiment-name e1 > ../timer/jsoncpp_exp1/stage02.log
# date > ../timer/jsoncpp_exp1/stage02_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 1077
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 201.28003406524658
# min: 3.354667234420776
# hour: 0.055911120573679605

# 614 usable buggy versions



# ===============================


# 3. Prepare prerequisites
# date > ../timer/jsoncpp_exp1/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject jsoncpp_exp1 --experiment-name e1 --version-limit 614 > ../timer/jsoncpp_exp1/stage03.log
# date > ../timer/jsoncpp_exp1/stage03_end-remote.txt

# Number of buggy versions: 614
# Number of tasks (assigned_works): 232
# Number of tasks (works): 614
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29


# sec: 288.29775857925415
# min: 4.80496264298757
# hour: 0.08008271071645949

# 598 valid prerequisites


# python3 validator.py --subject jsoncpp_exp1 --experiment-name e1 --validation-criteria 1,2,3,4,5,6,7



# ===============================

# 4. Extract SBFL features

# date > ../timer/jsoncpp_exp1/stage04_start-remote.txt
# time python3 extract_sbfl_features.py --subject jsoncpp_exp1 --experiment-name e1 --target-set-name prerequisite_data > ../timer/jsoncpp_exp1/stage04.log
# date > ../timer/jsoncpp_exp1/stage04_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 598
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 70.66028904914856
# min: 1.177671484152476
# hour: 0.019627858069207933

# 598 valid SBFL features

# python3 validator.py --subject jsoncpp_exp1 --experiment-name e1 --validation-criteria 8
# python3 analyzer.py --subject jsoncpp_exp1 --experiment-name e1 --analysis-criteria 1

# ===============================

# 5. Extract MBFL features

# date > ../timer/jsoncpp_exp1/stage05_start-remote.txt
# time python3 extract_mbfl_features.py --subject jsoncpp_exp1 --experiment-name e1 --target-set-name prerequisite_data --trial trial1 --parallel-cnt 2 --dont-terminate-leftovers --remain-one-bug-per-line --version-limit 232 > ../timer/jsoncpp_exp1/stage05.log
# date > ../timer/jsoncpp_exp1/stage05_end-remote.txt

# Number of buggy versions: 614
# Number of tasks (assigned_works): 232
# Number of tasks (works): 614
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 9143.332903623581
# min: 152.38888172705967
# hour: 2.5398146954509944

# extracted 232 valid MBFL features

# python3 validator.py --subject jsoncpp_exp1 --experiment-name e1 --validation-criteria 9,10,11,12
# python3 analyzer.py --subject jsoncpp_exp1 --experiment-name e1 --analysis-criteria 1


# ===============================

# cp ../configs/method0.json ../configs/analysis_config.json
# echo "analyzing jsoncpp_exp1 allfails-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject jsoncpp_exp1 --experiment-name e1 --analysis-criteria 2 --type-name allfails-noReduced-excludeCCT-noHeuristics

# *

# cp ../configs/method1-50.json ../configs/analysis_config.json
# echo "analyzing jsoncpp_exp1 rand50-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject jsoncpp_exp1 --experiment-name e1 --analysis-criteria 2 --type-name rand50-noReduced-excludeCCT-noHeuristics

# cp ../configs/method1-30.json ../configs/analysis_config.json
# echo "analyzing jsoncpp_exp1 rand30-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject jsoncpp_exp1 --experiment-name e1 --analysis-criteria 2 --type-name rand30-noReduced-excludeCCT-noHeuristics

# *

# cp ../configs/method2-50.json ../configs/analysis_config.json
# echo "analyzing jsoncpp_exp1 sbflnaish250-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject jsoncpp_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-noReduced-excludeCCT-noHeuristics

# cp ../configs/method2-30.json ../configs/analysis_config.json
# echo "analyzing jsoncpp_exp1 sbflnaish230-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject jsoncpp_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-noReduced-excludeCCT-noHeuristics

# *

# cp ../configs/method3-50-avg.json ../configs/analysis_config.json
# echo "analyzing jsoncpp_exp1 sbflnaish250-reduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject jsoncpp_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-reduced-excludeCCT-noHeuristics

# cp ../configs/method3-30-avg.json ../configs/analysis_config.json
# echo "analyzing jsoncpp_exp1 sbflnaish230-reduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject jsoncpp_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-reduced-excludeCCT-noHeuristics

# *

# cp ../configs/method4-50-sbfl.json ../configs/analysis_config.json
# echo "analyzing jsoncpp_exp1 sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject jsoncpp_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics

# cp ../configs/method4-30-sbfl.json ../configs/analysis_config.json
# echo "analyzing jsoncpp_exp1 sbflnaish230-reduced_sbflnaish2-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject jsoncpp_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-reduced_sbflnaish2-excludeCCT-noHeuristics

# ===============================

time python3 analyzer.py \
    --subject jsoncpp_exp1 \
    --experiment-name e1 \
    --analysis-criteria 9 \
    --batch-size 512

# time python3 analyzer.py \
#     --subject jsoncpp_exp1 \
#     --experiment-name e1 \
#     --analysis-criteria 8

# time python3 analyzer.py \
#     --subject jsoncpp_exp1 \
#     --experiment-name e1 \
#     --analysis-criteria 9 \
#     --batch-size 512