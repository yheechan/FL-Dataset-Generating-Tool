# 1. Collect buggy mutants
# date > ../timer/opencv_calib3d_exp1/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject opencv_calib3d_exp1 --experiment-name e1 > ../timer/opencv_calib3d_exp1/stage01.log
# date > ../timer/opencv_calib3d_exp1/stage01_end-remote.txt

# Number of tasks (assigned-stage01): 2194
# Number of tasks (mutants-stage01): 4446
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 7140.272825241089
# min: 119.00454708735148
# hour: 1.9834091181225246

# 1376 buggy mutants

# ===============================


# 2. Select usable versions
# date > ../timer/opencv_calib3d_exp1/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject opencv_calib3d_exp1 --experiment-name e1 > ../timer/opencv_calib3d_exp1/stage02.log
# date > ../timer/opencv_calib3d_exp1/stage02_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 1376
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 1479.677903175354
# min: 24.6612983862559
# hour: 0.4110216397709317

# 1012 usable buggy versions



# ===============================


# 3. Prepare prerequisites
# date > ../timer/opencv_calib3d_exp1/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject opencv_calib3d_exp1 --experiment-name e1 --version-limit 1012 > ../timer/opencv_calib3d_exp1/stage03.log
# date > ../timer/opencv_calib3d_exp1/stage03_end-remote.txt


# Number of buggy versions: 1012
# Number of tasks (assigned_works): 232
# Number of tasks (works): 1012
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 2424.945074558258
# min: 40.41575124263763
# hour: 0.6735958540439605

# 1009 valid prerequisites


# python3 validator.py --subject libxml2_exp1 --experiment-name e1 --validation-criteria 1,2,3,4,5,6,7



# ===============================

# 4. Extract SBFL features

# date > ../timer/opencv_calib3d_exp1/stage04_start-remote.txt
# time python3 extract_sbfl_features.py --subject opencv_calib3d_exp1 --experiment-name e1 --target-set-name prerequisite_data > ../timer/opencv_calib3d_exp1/stage04.log
# date > ../timer/opencv_calib3d_exp1/stage04_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 1009
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 238.0125732421875
# min: 3.966876220703125
# hour: 0.06611460367838543

# 1009 valid SBFL features

# python3 validator.py --subject libxml2_exp1 --experiment-name e1 --validation-criteria 8
# python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 1

# ===============================

# 5. Extract MBFL features

# date > ../timer/opencv_calib3d_exp1/stage05_start-remote.txt
# time python3 extract_mbfl_features.py --subject opencv_calib3d_exp1 --experiment-name e1 --target-set-name prerequisite_data --trial trial1 --parallel-cnt 2 --dont-terminate-leftovers --remain-one-bug-per-line --version-limit 232 > ../timer/opencv_calib3d_exp1/stage05.log
# date > ../timer/opencv_calib3d_exp1/stage05_end-remote.txt


# Number of tasks (assigned_works): 232
# Number of tasks (works): 232
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29


# sec: 78959.50080251694
# min: 1315.991680041949
# hour: 21.933194667365814


# extracted 232 valid MBFL features

# python3 validator.py --subject libxml2_exp1 --experiment-name e1 --validation-criteria 9,10,11,12
# python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 1
# python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 4



# =============================== 50%
# echo "analyzing opencv_calib3d_exp1 allfails-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_calib3d_exp1 --experiment-name e1 --analysis-criteria 2 --type-name allfails-noReduced-excludeCCT-noHeuristics

# echo "analyzing opencv_calib3d_exp1 rand50-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_calib3d_exp1 --experiment-name e1 --analysis-criteria 2 --type-name rand50-noReduced-excludeCCT-noHeuristics

# =============================== 30%

# echo "analyzing opencv_calib3d_exp1 rand30-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_calib3d_exp1 --experiment-name e1 --analysis-criteria 2 --type-name rand30-noReduced-excludeCCT-noHeuristics

# echo "analyzing opencv_calib3d_exp1 sbflnaish230-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_calib3d_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-noReduced-excludeCCT-noHeuristics

# ===============================

# echo "analyzing opencv_calib3d_exp1 sbflnaish250-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_calib3d_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-noReduced-excludeCCT-noHeuristics

# echo "analyzing opencv_calib3d_exp1 sbflnaish250-reduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_calib3d_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-reduced-excludeCCT-noHeuristics

# echo "analyzing opencv_calib3d_exp1 sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_calib3d_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics


# =============================== 30%

# echo "analyzing opencv_calib3d_exp1 sbflnaish230-reduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_calib3d_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-reduced-excludeCCT-noHeuristics

# echo "analyzing opencv_calib3d_exp1 sbflnaish230-reduced_sbflnaish2-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_calib3d_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-reduced_sbflnaish2-excludeCCT-noHeuristics



# ===============================

# time python3 analyzer.py \
#     --subject opencv_calib3d_exp1 \
#     --experiment-name e1 \
#     --analysis-criteria 9 \
#     --batch-size 512


# time python3 analyzer.py \
#     --subject opencv_calib3d_exp1 \
#     --experiment-name e1 \
#     --analysis-criteria 8

# time python3 analyzer.py \
#     --subject opencv_calib3d_exp1 \
#     --experiment-name e1 \
#     --analysis-criteria 9 \
#     --batch-size 512
