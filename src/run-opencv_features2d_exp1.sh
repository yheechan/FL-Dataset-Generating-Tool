# 1. Collect buggy mutants
# date > ../timer/opencv_features2d_exp1/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject opencv_features2d_exp1 --experiment-name e1 > ../timer/opencv_features2d_exp1/stage01.log
# date > ../timer/opencv_features2d_exp1/stage01_end-remote.txt

# Number of tasks (assigned-stage01): 987
# Number of tasks (mutants-stage01): 2258
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 4036.4831805229187
# min: 67.27471967538197
# hour: 1.121245327923033

# 560 buggy mutants

# ===============================


# 2. Select usable versions
# date > ../timer/opencv_features2d_exp1/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject opencv_features2d_exp1 --experiment-name e1 > ../timer/opencv_features2d_exp1/stage02.log
# date > ../timer/opencv_features2d_exp1/stage02_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 560
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 1238.2325401306152
# min: 20.63720900217692
# hour: 0.34395348336961534

# 318 usable buggy versions



# ===============================


# 3. Prepare prerequisites
# date > ../timer/opencv_features2d_exp1/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject opencv_features2d_exp1 --experiment-name e1 --version-limit 618 > ../timer/opencv_features2d_exp1/stage03.log
# date > ../timer/opencv_features2d_exp1/stage03_end-remote.txt


# Number of buggy versions: 318
# Number of tasks (assigned_works): 232
# Number of tasks (works): 318
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 1329.083848953247
# min: 22.151397482554117
# hour: 0.3691899580425686

# 310 valid prerequisites


# python3 validator.py --subject libxml2_exp1 --experiment-name e1 --validation-criteria 1,2,3,4,5,6,7



# ===============================

# 4. Extract SBFL features

# date > ../timer/opencv_features2d_exp1/stage04_start-remote.txt
# time python3 extract_sbfl_features.py --subject opencv_features2d_exp1 --experiment-name e1 --target-set-name prerequisite_data > ../timer/opencv_features2d_exp1/stage04.log
# date > ../timer/opencv_features2d_exp1/stage04_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 310
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 72.61860299110413
# min: 1.2103100498517354
# hour: 0.02017183416419559

# 310 valid SBFL features

# python3 validator.py --subject libxml2_exp1 --experiment-name e1 --validation-criteria 8
# python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 1

# ===============================

# 5. Extract MBFL features

# date > ../timer/opencv_features2d_exp1/stage05_start-remote.txt
# time python3 extract_mbfl_features.py --subject opencv_features2d_exp1 --experiment-name e1 --target-set-name prerequisite_data --trial trial1 --parallel-cnt 2 --dont-terminate-leftovers --remain-one-bug-per-line --version-limit 232 > ../timer/opencv_features2d_exp1/stage05.log
# date > ../timer/opencv_features2d_exp1/stage05_end-remote.txt

# sec: 44459.64523410797
# min: 740.9940872351328
# hour: 12.34990145391888

# Number of tasks (assigned_works): 232
# Number of tasks (works): 232
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29


# extracted 232 valid MBFL features

# python3 validator.py --subject libxml2_exp1 --experiment-name e1 --validation-criteria 9,10,11,12
# python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 1
# python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 4



# =============================== 50%
# echo "analyzing opencv_features2d_exp1 allfails-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_features2d_exp1 --experiment-name e1 --analysis-criteria 2 --type-name allfails-noReduced-excludeCCT-noHeuristics

# echo "analyzing opencv_features2d_exp1 rand50-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_features2d_exp1 --experiment-name e1 --analysis-criteria 2 --type-name rand50-noReduced-excludeCCT-noHeuristics

# =============================== 30%

# echo "analyzing opencv_features2d_exp1 rand30-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_features2d_exp1 --experiment-name e1 --analysis-criteria 2 --type-name rand30-noReduced-excludeCCT-noHeuristics

# echo "analyzing opencv_features2d_exp1 sbflnaish230-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_features2d_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-noReduced-excludeCCT-noHeuristics

# ===============================

# echo "analyzing opencv_features2d_exp1 sbflnaish250-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_features2d_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-noReduced-excludeCCT-noHeuristics

# echo "analyzing opencv_features2d_exp1 sbflnaish250-reduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_features2d_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-reduced-excludeCCT-noHeuristics

# echo "analyzing opencv_features2d_exp1 sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_features2d_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics


# =============================== 30%

# echo "analyzing opencv_features2d_exp1 sbflnaish230-reduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_features2d_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-reduced-excludeCCT-noHeuristics

# echo "analyzing opencv_features2d_exp1 sbflnaish230-reduced_sbflnaish2-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_features2d_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-reduced_sbflnaish2-excludeCCT-noHeuristics



# ===============================

time python3 analyzer.py \
    --subject opencv_features2d_exp1 \
    --experiment-name e1 \
    --analysis-criteria 9 \
    --batch-size 512


# time python3 analyzer.py \
#     --subject opencv_features2d_exp1 \
#     --experiment-name e1 \
#     --analysis-criteria 8

# time python3 analyzer.py \
#     --subject opencv_features2d_exp1 \
#     --experiment-name e1 \
#     --analysis-criteria 9 \
#     --batch-size 512