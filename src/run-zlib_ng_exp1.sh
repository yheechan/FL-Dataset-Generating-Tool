# 1. Collect buggy mutants
# date > ../timer/zlib_ng_exp1/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject zlib_ng_exp1 --experiment-name e1 > ../timer/zlib_ng_exp1/stage01.log
# date > ../timer/zlib_ng_exp1/stage01_end-remote.txt


# Number of tasks (assigned-stage01): 1789
# Number of tasks (mutants-stage01): 4840
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 1175.8687601089478
# min: 19.59781266848246
# hour: 0.32663021114137436

# 2499 buggy mutants

# ===============================


# 2. Select usable versions
# date > ../timer/zlib_ng_exp1/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject zlib_ng_exp1 --experiment-name e1 > ../timer/zlib_ng_exp1/stage02.log
# date > ../timer/zlib_ng_exp1/stage02_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 2499
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 282.8641052246094
# min: 4.7144017537434895
# hour: 0.07857336256239149

# 1441 usable buggy versions



# ===============================


# 3. Prepare prerequisites
# date > ../timer/zlib_ng_exp1/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject zlib_ng_exp1 --experiment-name e1 --version-limit 1441 > ../timer/zlib_ng_exp1/stage03.log
# date > ../timer/zlib_ng_exp1/stage03_end-remote.txt


# Number of buggy versions: 1441
# Number of tasks (assigned_works): 232
# Number of tasks (works): 464
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 379.4492688179016
# min: 6.32415448029836
# hour: 0.10540257467163934

# 1414 valid prerequisites

# python3 validator.py --subject libxml2_exp1 --experiment-name e1 --validation-criteria 1,2,3,4,5,6,7

# ===============================

# 4. Extract SBFL features

# date > ../timer/zlib_ng_exp1/stage04_start-remote.txt
# time python3 extract_sbfl_features.py --subject zlib_ng_exp1 --experiment-name e1 --target-set-name prerequisite_data > ../timer/zlib_ng_exp1/stage04.log
# date > ../timer/zlib_ng_exp1/stage04_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 448
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 24.63421082496643
# min: 0.41057018041610716
# hour: 0.006842836340268453

# 1414 valid SBFL features

# python3 validator.py --subject libxml2_exp1 --experiment-name e1 --validation-criteria 8
# python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 1


# ===============================

# 5. Extract MBFL features

# date > ../timer/zlib_ng_exp1/stage05_start-remote.txt
# time python3 extract_mbfl_features.py --subject zlib_ng_exp1 --experiment-name e1 --target-set-name prerequisite_data --trial trial1 --parallel-cnt 2 --dont-terminate-leftovers --version-limit 448 --remain-one-bug-per-line > ../timer/zlib_ng_exp1/stage05.log
# date > ../timer/zlib_ng_exp1/stage05_end-remote.txt

# Number of tasks (assigned_works): 240
# Number of tasks (works): 167
# Number of tasks (repo): 240
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30

# sec: 11392.129829406738
# min: 189.86883049011232
# hour: 3.1644805081685385


# extracted 157 valid MBFL features


# python3 validator.py --subject libxml2_exp1 --experiment-name e1 --validation-criteria 9,10,11,12
# python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 1
# python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 4



# =============================== 50%

# echo "analyzing zlib_ng_exp1 allfails-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_exp1 --experiment-name e1 --analysis-criteria 2 --type-name allfails-noReduced-excludeCCT-noHeuristics

# echo "analyzing zlib_ng_exp1 rand50-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_exp1 --experiment-name e1 --analysis-criteria 2 --type-name rand50-noReduced-excludeCCT-noHeuristics


# =============================== 30%

# echo "analyzing zlib_ng_exp1 rand30-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_exp1 --experiment-name e1 --analysis-criteria 2 --type-name rand30-noReduced-excludeCCT-noHeuristics

# echo "analyzing zlib_ng_exp1 sbflnaish230-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-noReduced-excludeCCT-noHeuristics

# ===============================

# echo "analyzing zlib_ng_exp1 sbflnaish250-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-noReduced-excludeCCT-noHeuristics

# echo "analyzing zlib_ng_exp1 sbflnaish250-reduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-reduced-excludeCCT-noHeuristics

# echo "analyzing zlib_ng_exp1 sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics

# =============================== 30%

# echo "analyzing zlib_ng_exp1 sbflnaish230-reduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-reduced-excludeCCT-noHeuristics

# echo "analyzing zlib_ng_exp1 sbflnaish230-reduced_sbflnaish2-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-reduced_sbflnaish2-excludeCCT-noHeuristics


# ===============================


# time python3 analyzer.py \
#     --subject zlib_ng_exp1 \
#     --experiment-name e1 \
#     --analysis-criteria 9 \
#     --batch-size 128

# time python3 analyzer.py \
#     --subject zlib_ng_exp1 \
#     --experiment-name e1 \
#     --analysis-criteria 8


# time python3 analyzer.py \
#     --subject zlib_ng_exp1 \
#     --experiment-name e1 \
#     --analysis-criteria 9 \
#     --batch-size 128
