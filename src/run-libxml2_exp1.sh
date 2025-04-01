# 1. Collect buggy mutants
# date > ../timer/libxml2_exp1/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject libxml2_exp1 --experiment-name e1 > ../timer/libxml2_exp1/stage01.log
# date > ../timer/libxml2_exp1/stage01_end-remote.txt


# Number of tasks (assigned-stage01): 1147
# Number of tasks (mutants-stage01): 7457
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 1244.455531835556
# min: 20.7409255305926
# hour: 0.3456820921765434

# 1619 buggy mutants

# ===============================


# 2. Select usable versions
# date > ../timer/libxml2_exp1/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject libxml2_exp1 --experiment-name e1 > ../timer/libxml2_exp1/stage02.log
# date > ../timer/libxml2_exp1/stage02_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 2122
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 308.2935667037964
# min: 5.1382261117299395
# hour: 0.08563710186216565


# 1415 usable buggy versions



# ===============================


# 3. Prepare prerequisites
# date > ../timer/libxml2_exp1/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject libxml2_exp1 --experiment-name e1 --version-limit 464 > ../timer/libxml2_exp1/stage03.log
# date > ../timer/libxml2_exp1/stage03_end-remote.txt


# Number of buggy versions: 1270
# Number of tasks (assigned_works): 232
# Number of tasks (works): 464
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 418.90068221092224
# min: 6.981678036848704
# hour: 0.11636130061414507

# 456 valid prerequisites


# python3 validator.py --subject libxml2_exp1 --experiment-name e1 --validation-criteria 1,2,3,4,5,6,7



# ===============================

# 4. Extract SBFL features

# date > ../timer/libxml2_exp1/stage04_start-remote.txt
# time python3 extract_sbfl_features.py --subject libxml2_exp1 --experiment-name e1 --target-set-name prerequisite_data > ../timer/libxml2_exp1/stage04.log
# date > ../timer/libxml2_exp1/stage04_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 404
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 198.54478240013123
# min: 3.3090797066688538
# hour: 0.055151328444480896

# 456 valid SBFL features

# python3 validator.py --subject libxml2_exp1 --experiment-name e1 --validation-criteria 8
# python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 1

# ===============================

# 5. Extract MBFL features

# date > ../timer/libxml2_exp1/stage05_start-remote.txt
# time python3 extract_mbfl_features.py --subject libxml2_exp1 --experiment-name e1 --target-set-name prerequisite_data --trial trial1 --parallel-cnt 5 --dont-terminate-leftovers --remain-one-bug-per-line --version-limit 8 > ../timer/libxml2_exp1/stage05.log
# date > ../timer/libxml2_exp1/stage05_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 236
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 64299.37897968292
# min: 1071.6563163280487
# hour: 17.860938605467478

# extracted 232 valid MBFL features

# python3 validator.py --subject libxml2_exp1 --experiment-name e1 --validation-criteria 9,10,11,12
# python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 1
# python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 4


# =============================== 50%

# echo "analyzing libxml2_exp1 allfails-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 2 --type-name allfails-noReduced-excludeCCT-noHeuristics

# echo "analyzing libxml2_exp1 rand50-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 2 --type-name rand50-noReduced-excludeCCT-noHeuristics

# =============================== 30%

# echo "analyzing libxml2_exp1 rand30-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 2 --type-name rand30-noReduced-excludeCCT-noHeuristics

# echo "analyzing libxml2_exp1 sbflnaish230-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-noReduced-excludeCCT-noHeuristics

# ===============================

# echo "analyzing libxml2_exp1 sbflnaish250-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-noReduced-excludeCCT-noHeuristics

# echo "analyzing libxml2_exp1 sbflnaish250-reduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-reduced-excludeCCT-noHeuristics

# echo "analyzing libxml2_exp1 sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics

# =============================== 30%

# echo "analyzing libxml2_exp1 sbflnaish230-reduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-reduced-excludeCCT-noHeuristics

# echo "analyzing libxml2_exp1 sbflnaish230-reduced_sbflnaish2-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-reduced_sbflnaish2-excludeCCT-noHeuristics


# ===============================

time python3 analyzer.py \
    --subject libxml2_exp1 \
    --experiment-name e1 \
    --analysis-criteria 9 \
    --batch-size 1024

# time python3 analyzer.py \
#     --subject libxml2_exp1 \
#     --experiment-name e1 \
#     --analysis-criteria 8

# time python3 analyzer.py \
#     --subject libxml2_exp1 \
#     --experiment-name e1 \
#     --analysis-criteria 9 \
#     --batch-size 1024