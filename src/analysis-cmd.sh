# 1. analyze the statiscis of mbfl versions
# python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 1
# python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 1


# mbfl results
# MBFL_METHOD: method1
# MAX_LINES_FOR_RANDOM: 50
# SBFL_RANKED_RATE: 0.3
# SBFL_STANDARD: gp13
# MUT_CNT_CONFIG: [2, 4, 6, 8, 10]
# EXPERIMENT_REPEAT: 5
# INCLUDE_CCT: False
# APPLY_HEURISTICS: False
# echo "analyzing opencv_features2d_TF_top30 rand50-exclude_cct-noHeuristics"
# time python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name rand50-exclude_cct-noHeuristics
# echo "analyzing opencv_features2d_TF_bot30 rand50-exclude_cct-noHeuristics"
# time python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name rand50-exclude_cct-noHeuristics
# echo "analyzing zlib_ng_TF_top30 rand50-exclude_cct-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name rand50-exclude_cct-noHeuristics
# echo "analyzing zlib_ng_TF_bot30 rand50-exclude_cct-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name rand50-exclude_cct-noHeuristics


# mbfl results
# MBFL_METHOD: method2
# MAX_LINES_FOR_RANDOM: 50
# SBFL_RANKED_RATE: 0.3
# SBFL_STANDARD: gp13
# MUT_CNT_CONFIG: [2, 4, 6, 8, 10]
# EXPERIMENT_REPEAT: 5
# INCLUDE_CCT: False
# APPLY_HEURISTICS: False
# echo "analyzing opencv_features2d_TF_top30 sbflrank30-exclude_cct-noHeuristics"
# time python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflrank30-exclude_cct-noHeuristics
# echo "analyzing opencv_features2d_TF_bot30 sbflrank30-exclude_cct-noHeuristics"
# time python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name sbflrank30-exclude_cct-noHeuristics
# echo "analyzing zlib_ng_TF_top30 sbflrank30-exclude_cct-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflrank30-exclude_cct-noHeuristics
# echo "analyzing zlib_ng_TF_bot30 sbflrank30-exclude_cct-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name sbflrank30-exclude_cct-noHeuristics

# 3. analyze rate of buggy line being in the top 30 sbfl ranked lines
# python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 3
# python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 3
# python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 3
# python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 3

# mbfl results
# MBFL_METHOD: method1
# MAX_LINES_FOR_RANDOM: 50
# SBFL_RANKED_RATE: 0.3
# SBFL_STANDARD: gp13
# MUT_CNT_CONFIG: [2, 4, 6, 8, 10]
# EXPERIMENT_REPEAT: 5
# INCLUDE_CCT: False
# APPLY_HEURISTICS: True
# echo "analyzing opencv_features2d_TF_top30 rand50-exclude_cct-applyHeuristics"
# time python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name rand50-exclude_cct-applyHeuristics
# 166
# echo "analyzing opencv_features2d_TF_bot30 rand50-exclude_cct-applyHeuristics"
# time python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name rand50-exclude_cct-applyHeuristics
# 95
# echo "analyzing zlib_ng_TF_top30 rand50-exclude_cct-applyHeuristics"
# time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name rand50-exclude_cct-applyHeuristics
# 141
# echo "analyzing zlib_ng_TF_bot30 rand50-exclude_cct-applyHeuristics"
# time python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name rand50-exclude_cct-applyHeuristics
# 141




python3 machine_learning.py --prepare-fl-features --subject zlib_ng_TF_bot30 --experiment-name TF_bot30
python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --train --project-name test1 --train-validate-test-ratio 6 2 2 --random-seed 42 --epoch 3 --batch-size 12 --device cuda --dropout 0.2 --model-shape 35 512 12 1