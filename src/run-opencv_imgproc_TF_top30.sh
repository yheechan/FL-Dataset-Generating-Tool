# 1. Collect buggy mutants
# date > ../timer/opencv_imgproc_TF_top30/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 > ../timer/opencv_imgproc_TF_top30/stage01.log
# date > ../timer/opencv_imgproc_TF_top30/stage01_end-remote.txt


# Number of tasks (assigned-stage01): 1948
# Number of tasks (mutants-stage01): 7837
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 4912.925967693329
# min: 81.88209946155548
# hour: 1.3647016576925914

# 3,004 buggy mutants

# ===============================


# 2. Select usable versions
# date > ../timer/opencv_imgproc_TF_top30/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 > ../timer/opencv_imgproc_TF_top30/stage02.log
# date > ../timer/opencv_imgproc_TF_top30/stage02_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 2000
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 1369.1290073394775
# min: 22.818816788991292
# hour: 0.38031361314985485


# 1376 usable buggy versions



# ===============================


# 3. Prepare prerequisites
# date > ../timer/opencv_imgproc_TF_top30/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --version-limit 464 > ../timer/opencv_imgproc_TF_top30/stage03.log
# date > ../timer/opencv_imgproc_TF_top30/stage03_end-remote.txt


# Number of buggy versions: 1376
# Number of tasks (assigned_works): 232
# Number of tasks (works): 464
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 1444.6272490024567
# min: 24.077120816707613
# hour: 0.40128534694512685

# 464 valid prerequisites


# python3 validator.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --validation-criteria 1,2,3,4,5,6



# ===============================

# 4. Extract SBFL features

# date > ../timer/opencv_imgproc_TF_top30/stage04_start-remote.txt
# time python3 extract_sbfl_features.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --target-set-name prerequisite_data > ../timer/opencv_imgproc_TF_top30/stage04.log
# date > ../timer/opencv_imgproc_TF_top30/stage04_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 778
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 105.62019538879395
# min: 1.7603365898132324
# hour: 0.029338943163553875

# 464 valid SBFL features

# python3 validator.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --validation-criteria 7
# python3 analyzer.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --analysis-criteria 1

# ===============================

# 5. Extract MBFL features

# date > ../timer/opencv_imgproc_TF_top30/stage05_start-remote.txt
# time python3 extract_mbfl_features.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --target-set-name prerequisite_data --trial trial1 --parallel-cnt 3 --dont-terminate-leftovers --remain-one-bug-per-line --version-limit 232 > ../timer/opencv_imgproc_TF_top30/stage05.log
# date > ../timer/opencv_imgproc_TF_top30/stage05_end-remote.txt

# Number of tasks (assigned_works): 232
# Number of tasks (works): 232
# Number of tasks (repo): 232
# Number of tasks (configurations): 29
# Number of tasks (src): 29
# Number of tasks (tools): 29
# Number of tasks (configurations): 29

# sec: 25232.122725963593
# min: 420.53537876605986
# hour: 7.008922979434331

# extracted 232 valid MBFL features

# python3 validator.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --validation-criteria 8,9,10
# python3 analyzer.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --analysis-criteria 4


# ===============================

echo "analyzing opencv_imgproc_TF_top30 sbflnaish250-noReduced-excludeCCT-noHeuristics"
time python3 analyzer.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish250-noReduced-excludeCCT-noHeuristics

# echo "analyzing opencv_imgproc_TF_top30 sbflnaish250-reduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish250-reduced-excludeCCT-noHeuristics

# echo "analyzing opencv_imgproc_TF_top30 sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics