# 1. Collect buggy mutants
# date > ../timer/jsoncpp_TF_top30/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject jsoncpp_TF_top30 --experiment-name TF_top30 > ../timer/jsoncpp_TF_top30/stage01.log
# date > ../timer/jsoncpp_TF_top30/stage01_end-remote.txt


# Number of tasks (assigned-stage01): 696
# Number of tasks (mutants-stage01): 2159
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 648.8220365047455
# min: 10.813700608412425
# hour: 0.18022834347354041

# 1073 buggy mutants

# ===============================


# 2. Select usable versions
# date > ../timer/jsoncpp_TF_top30/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject jsoncpp_TF_top30 --experiment-name TF_top30 > ../timer/jsoncpp_TF_top30/stage02.log
# date > ../timer/jsoncpp_TF_top30/stage02_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 1073
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 192.54021048545837
# min: 3.209003508090973
# hour: 0.05348339180151621

# 615 usable buggy versions



# ===============================


# 3. Prepare prerequisites
# date > ../timer/jsoncpp_TF_top30/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject jsoncpp_TF_top30 --experiment-name TF_top30 --version-limit 615 > ../timer/jsoncpp_TF_top30/stage03.log
# date > ../timer/jsoncpp_TF_top30/stage03_end-remote.txt

# Number of buggy versions: 615
# Number of tasks (assigned_works): 232
# Number of tasks (works): 615
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29


# sec: 294.33634424209595
# min: 4.9056057373682656
# hour: 0.08176009562280442

# 597 valid prerequisites


# python3 validator.py --subject jsoncpp_TF_top30 --experiment-name TF_top30 --validation-criteria 1,2,3,4,5,6



# ===============================

# 4. Extract SBFL features

# date > ../timer/jsoncpp_TF_top30/stage04_start-remote.txt
# time python3 extract_sbfl_features.py --subject jsoncpp_TF_top30 --experiment-name TF_top30 --target-set-name prerequisite_data > ../timer/jsoncpp_TF_top30/stage04.log
# date > ../timer/jsoncpp_TF_top30/stage04_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 597
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 67.37683987617493
# min: 1.1229473312695821
# hour: 0.018715788854493036

# 597 valid SBFL features

# python3 validator.py --subject jsoncpp_TF_top30 --experiment-name TF_top30 --validation-criteria 7
# python3 analyzer.py --subject jsoncpp_TF_top30 --experiment-name TF_top30 --analysis-criteria 1

# ===============================

# 5. Extract MBFL features

# date > ../timer/jsoncpp_TF_top30/stage05_start-remote.txt
# time python3 extract_mbfl_features.py --subject jsoncpp_TF_top30 --experiment-name TF_top30 --target-set-name prerequisite_data --trial trial1 --parallel-cnt 2 --dont-terminate-leftovers --remain-one-bug-per-line --version-limit 232 > ../timer/jsoncpp_TF_top30/stage05.log
# date > ../timer/jsoncpp_TF_top30/stage05_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 232
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 11345.339986801147
# min: 189.08899978001912
# hour: 3.1514833296669855

# extracted 232 valid MBFL features

# python3 validator.py --subject jsoncpp_TF_top30 --experiment-name TF_top30 --validation-criteria 8,9,10
# python3 analyzer.py --subject jsoncpp_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject jsoncpp_TF_top30 --experiment-name TF_top30 --analysis-criteria 4


# ===============================

# cp ../configs/method0.json ../configs/analysis_config.json
# echo "analyzing jsoncpp_TF_top30 allfails-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject jsoncpp_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name allfails-noReduced-excludeCCT-noHeuristics

# *

# cp ../configs/method1-50.json ../configs/analysis_config.json
# echo "analyzing jsoncpp_TF_top30 rand50-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject jsoncpp_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name rand50-noReduced-excludeCCT-noHeuristics

# cp ../configs/method1-30.json ../configs/analysis_config.json
# echo "analyzing jsoncpp_TF_top30 rand30-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject jsoncpp_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name rand30-noReduced-excludeCCT-noHeuristics

# *

# cp ../configs/method2-50.json ../configs/analysis_config.json
# echo "analyzing jsoncpp_TF_top30 sbflnaish250-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject jsoncpp_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish250-noReduced-excludeCCT-noHeuristics

# cp ../configs/method2-30.json ../configs/analysis_config.json
# echo "analyzing jsoncpp_TF_top30 sbflnaish230-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject jsoncpp_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish230-noReduced-excludeCCT-noHeuristics

# *

# cp ../configs/method3-50-avg.json ../configs/analysis_config.json
# echo "analyzing jsoncpp_TF_top30 sbflnaish250-reduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject jsoncpp_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish250-reduced-excludeCCT-noHeuristics

# cp ../configs/method3-30-avg.json ../configs/analysis_config.json
# echo "analyzing jsoncpp_TF_top30 sbflnaish230-reduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject jsoncpp_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish230-reduced-excludeCCT-noHeuristics

# *

# cp ../configs/method4-50-sbfl.json ../configs/analysis_config.json
# echo "analyzing jsoncpp_TF_top30 sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject jsoncpp_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics

# cp ../configs/method4-30-sbfl.json ../configs/analysis_config.json
# echo "analyzing jsoncpp_TF_top30 sbflnaish230-reduced_sbflnaish2-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject jsoncpp_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish230-reduced_sbflnaish2-excludeCCT-noHeuristics

# ===============================

time python3 analyzer.py \
    --subject jsoncpp_TF_top30 \
    --experiment-name TF_top30 \
    --analysis-criteria 9 \
    --batch-size 512

# time python3 analyzer.py \
#     --subject jsoncpp_TF_top30 \
#     --experiment-name TF_top30 \
#     --analysis-criteria 8

# time python3 analyzer.py \
#     --subject jsoncpp_TF_top30 \
#     --experiment-name TF_top30 \
#     --analysis-criteria 9 \
#     --batch-size 512