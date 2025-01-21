# 1. analyze the statiscis of mbfl versions
# python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 1
# python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 1


# ================== FL analysis ==================

# mbfl results
# cp ../configs/exp1.json ../configs/analysis_config.json
# echo "analyzing opencv_features2d_TF_top30 allfails-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name allfails-excludeCCT-noHeuristics
# echo "analyzing opencv_features2d_TF_bot30 allfails-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name allfails-excludeCCT-noHeuristics
# echo "analyzing zlib_ng_TF_top30 allfails-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name allfails-excludeCCT-noHeuristics
# echo "analyzing zlib_ng_TF_bot30 allfails-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name allfails-excludeCCT-noHeuristics

# cp ../configs/exp2.json ../configs/analysis_config.json
# echo "analyzing opencv_features2d_TF_top30 rand20-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name rand20-excludeCCT-noHeuristics
# echo "analyzing opencv_features2d_TF_bot30 rand20-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name rand20-excludeCCT-noHeuristics
# echo "analyzing zlib_ng_TF_top30 rand20-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name rand20-excludeCCT-noHeuristics
# echo "analyzing zlib_ng_TF_bot30 rand20-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name rand20-excludeCCT-noHeuristics

# cp ../configs/exp3.json ../configs/analysis_config.json
# echo "analyzing opencv_features2d_TF_top30 sbflnaish220-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish220-excludeCCT-noHeuristics
# echo "analyzing opencv_features2d_TF_bot30 sbflnaish220-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name sbflnaish220-excludeCCT-noHeuristics
# echo "analyzing zlib_ng_TF_top30 sbflnaish220-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish220-excludeCCT-noHeuristics
# echo "analyzing zlib_ng_TF_bot30 sbflnaish220-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name sbflnaish220-excludeCCT-noHeuristics




# # 3. analyze rate of buggy line being in the top 30 sbfl ranked lines
# python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 3
# python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 3
# python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 3
# python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 3



# ================== machine learning ==================

# ================== M1 ==================
# train model: M1
# time python3 machine_learning.py \
#     --subject opencv_features2d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-excludeCCT-noHeuristics \
#     --project-name allfails-excludeCCT-noHeuristics-t1 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 20 \
#     --batch-size 256 \
#     --device cuda \
#     --dropout 0.2 \
#     --model-shape 36 64 64 32 1

# time python3 machine_learning.py \
#     --subject opencv_features2d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-excludeCCT-noHeuristics \
#     --inference-name self-D1 \
#     --inference \
#     --model-name opencv_features2d_TF_top30::allfails-excludeCCT-noHeuristics-t1 \
#     --device cuda


# ================== M2 ==================
# # train model: M2
# time python3 machine_learning.py \
#     --subject opencv_features2d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name rand20-excludeCCT-noHeuristics \
#     --project-name rand20-excludeCCT-noHeuristics-train1 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 20 \
#     --batch-size 256 \
#     --device cuda \
#     --dropout 0.2 \
#     --model-shape 35 64 64 32 1



# ================== M3 ==================
# train model: M3
# time python3 machine_learning.py \
#     --subject opencv_features2d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name sbflgp13-excludeCCT-noHeuristics-delibIncl \
#     --project-name sbflgp13-excludeCCT-noHeuristics-delibIncl-train1 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 20 \
#     --batch-size 256 \
#     --device cuda \
#     --dropout 0.2 \
#     --model-shape 35 64 64 32 1

# ================== M4 ==================
# # train model: M4
# time python3 machine_learning.py \
#     --subject opencv_features2d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl \
#     --project-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl-train2 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 30 \
#     --batch-size 256 \
#     --device cuda \
#     --dropout 0.2 \
#     --model-shape 35 64 64 32 1

# time python3 machine_learning.py \
#     --subject opencv_features2d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl \
#     --inference-name self-D4 \
#     --inference \
#     --model-name opencv_features2d_TF_top30::sbflgp13-excludeCCT-noHeuristics-noDelibIncl-train2 \
#     --device cuda

# python3 ML_analysis_script.py \
#     --model-name opencv_features2d_TF_top30::sbflgp13-excludeCCT-noHeuristics-noDelibIncl-train2 \
#     --model-id D4


# ================== M5 ==================
# train model: M5
# time python3 machine_learning.py \
#     --subject zlib_ng_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name rand50-excludeCCT-noHeuristics-delibIncl \
#     --project-name rand50-excludeCCT-noHeuristics-delibIncl-train3 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 10 \
#     --batch-size 128 \
#     --device cuda \
#     --dropout 0.2 \
#     --model-shape 35 64 32 1

# time python3 machine_learning.py \
#     --subject zlib_ng_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name rand50-excludeCCT-noHeuristics-delibIncl \
#     --inference-name self-D5 \
#     --inference \
#     --model-name zlib_ng_TF_top30::rand50-excludeCCT-noHeuristics-delibIncl-train3 \
#     --device cuda

# python3 ML_analysis_script.py \
#     --model-name zlib_ng_TF_top30::rand50-excludeCCT-noHeuristics-delibIncl-train3 \
#     --model-id D5


# ================== M6 ==================
# # train model: M6
# time python3 machine_learning.py \
#     --subject zlib_ng_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name rand50-excludeCCT-noHeuristics-noDelibIncl \
#     --project-name rand50-excludeCCT-noHeuristics-noDelibIncl-train1 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 10 \
#     --batch-size 128 \
#     --device cuda \
#     --dropout 0.2 \
#     --model-shape 35 64 32 1

# time python3 machine_learning.py \
#     --subject zlib_ng_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name rand50-excludeCCT-noHeuristics-noDelibIncl \
#     --inference-name self-D6 \
#     --inference \
#     --model-name zlib_ng_TF_top30::rand50-excludeCCT-noHeuristics-noDelibIncl-train1 \
#     --device cuda

# python3 ML_analysis_script.py \
#     --model-name zlib_ng_TF_top30::rand50-excludeCCT-noHeuristics-noDelibIncl-train1 \
#     --model-id D6

# ================== M7 ==================
# train model: M7
# time python3 machine_learning.py \
#     --subject zlib_ng_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name sbflgp13-excludeCCT-noHeuristics-delibIncl \
#     --project-name sbflgp13-excludeCCT-noHeuristics-delibIncl-train1 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 10 \
#     --batch-size 128 \
#     --device cuda \
#     --dropout 0.2 \
#     --model-shape 35 64 32 1

# time python3 machine_learning.py \
#     --subject zlib_ng_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name sbflgp13-excludeCCT-noHeuristics-delibIncl \
#     --inference-name self-D7 \
#     --inference \
#     --model-name zlib_ng_TF_top30::sbflgp13-excludeCCT-noHeuristics-delibIncl-train1 \
#     --device cuda

# python3 ML_analysis_script.py \
#     --model-name zlib_ng_TF_top30::sbflgp13-excludeCCT-noHeuristics-delibIncl-train1 \
#     --model-id D7


# ================== M8 ==================
# # train model: M8
# time python3 machine_learning.py \
#     --subject zlib_ng_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl \
#     --project-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl-train1 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 10 \
#     --batch-size 128 \
#     --device cuda \
#     --dropout 0.2 \
#     --model-shape 35 64 32 1

# time python3 machine_learning.py \
#     --subject zlib_ng_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl \
#     --inference-name self-D8 \
#     --inference \
#     --model-name zlib_ng_TF_top30::sbflgp13-excludeCCT-noHeuristics-noDelibIncl-train1 \
#     --device cuda

# python3 ML_analysis_script.py \
#     --model-name zlib_ng_TF_top30::sbflgp13-excludeCCT-noHeuristics-noDelibIncl-train1 \
#     --model-id D8

