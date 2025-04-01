# 1. Collect buggy mutants
# date > ../timer/opencv_imgproc_exp1/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject opencv_imgproc_exp1 --experiment-name e1 > ../timer/opencv_imgproc_exp1/stage01.log
# date > ../timer/opencv_imgproc_exp1/stage01_end-remote.txt

# Number of tasks (assigned-stage01): 1447
# Number of tasks (mutants-stage01): 1758
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 4374.17924785614
# min: 72.902987464269
# hour: 1.21504979107115

# 610 buggy mutants

# ===============================


# 2. Select usable versions
# date > ../timer/opencv_imgproc_exp1/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject opencv_imgproc_exp1 --experiment-name e1 > ../timer/opencv_imgproc_exp1/stage02.log
# date > ../timer/opencv_imgproc_exp1/stage02_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 610
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 1205.9945499897003
# min: 20.099909166495006
# hour: 0.3349984861082501

# 429 usable buggy versions



# ===============================


# 3. Prepare prerequisites
# date > ../timer/opencv_imgproc_exp1/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject opencv_imgproc_exp1 --experiment-name e1 --version-limit 618 > ../timer/opencv_imgproc_exp1/stage03.log
# date > ../timer/opencv_imgproc_exp1/stage03_end-remote.txt


# Number of buggy versions: 429
# Number of tasks (assigned_works): 232
# Number of tasks (works): 429
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 1419.1689012050629
# min: 23.652815020084383
# hour: 0.394213583668073

# 429 valid prerequisites


# python3 validator.py --subject libxml2_exp1 --experiment-name e1 --validation-criteria 1,2,3,4,5,6,7



# ===============================

# 4. Extract SBFL features

# date > ../timer/opencv_imgproc_exp1/stage04_start-remote.txt
# time python3 extract_sbfl_features.py --subject opencv_imgproc_exp1 --experiment-name e1 --target-set-name prerequisite_data > ../timer/opencv_imgproc_exp1/stage04.log
# date > ../timer/opencv_imgproc_exp1/stage04_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 429
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 79.47074508666992
# min: 1.3245124181111654
# hour: 0.022075206968519424

# 429 valid SBFL features

# python3 validator.py --subject libxml2_exp1 --experiment-name e1 --validation-criteria 8
# python3 analyzer.py --subject libxml2_exp1 --experiment-name e1 --analysis-criteria 1

# ===============================

# 5. Extract MBFL features

# date > ../timer/opencv_imgproc_exp1/stage05_start-remote.txt
# time python3 extract_mbfl_features.py --subject opencv_imgproc_exp1 --experiment-name e1 --target-set-name prerequisite_data --trial trial1 --parallel-cnt 8 --dont-terminate-leftovers --remain-one-bug-per-line --version-limit 1 > ../timer/opencv_imgproc_exp1/stage05-v1.log
# date > ../timer/opencv_imgproc_exp1/stage05_end-remote.txt

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
# echo "analyzing opencv_imgproc_exp1 allfails-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_imgproc_exp1 --experiment-name e1 --analysis-criteria 2 --type-name allfails-noReduced-excludeCCT-noHeuristics

# echo "analyzing opencv_imgproc_exp1 rand50-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_imgproc_exp1 --experiment-name e1 --analysis-criteria 2 --type-name rand50-noReduced-excludeCCT-noHeuristics

# =============================== 30%

# echo "analyzing opencv_imgproc_exp1 rand30-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_imgproc_exp1 --experiment-name e1 --analysis-criteria 2 --type-name rand30-noReduced-excludeCCT-noHeuristics

# echo "analyzing opencv_imgproc_exp1 sbflnaish230-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_imgproc_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-noReduced-excludeCCT-noHeuristics

# ===============================

# echo "analyzing opencv_imgproc_exp1 sbflnaish250-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_imgproc_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-noReduced-excludeCCT-noHeuristics

# echo "analyzing opencv_imgproc_exp1 sbflnaish250-reduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_imgproc_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-reduced-excludeCCT-noHeuristics

# echo "analyzing opencv_imgproc_exp1 sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_imgproc_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics


# =============================== 30%

# echo "analyzing opencv_imgproc_exp1 sbflnaish230-reduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_imgproc_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-reduced-excludeCCT-noHeuristics

# echo "analyzing opencv_imgproc_exp1 sbflnaish230-reduced_sbflnaish2-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_imgproc_exp1 --experiment-name e1 --analysis-criteria 2 --type-name sbflnaish230-reduced_sbflnaish2-excludeCCT-noHeuristics



# ===============================

time python3 analyzer.py \
    --subject opencv_imgproc_exp1 \
    --experiment-name e1 \
    --analysis-criteria 9 \
    --batch-size 512


# time python3 analyzer.py \
#     --subject opencv_imgproc_exp1 \
#     --experiment-name e1 \
#     --analysis-criteria 8

# time python3 analyzer.py \
#     --subject opencv_imgproc_exp1 \
#     --experiment-name e1 \
#     --analysis-criteria 9 \
#     --batch-size 512