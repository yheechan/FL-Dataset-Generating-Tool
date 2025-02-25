# 1. analyze the statiscis of mbfl versions
# python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject libxml2_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject opencv_calib3d_TF_top30 --experiment-name TF_top30 --analysis-criteria 1


# ================== FL analysis ==================

# mbfl results

# ******************************************

# cp ../configs/line_sel_00.json ../configs/analysis_config.json
# cp ../configs/line_sel_01.json ../configs/analysis_config.json
# cp ../configs/mut_num_00.json ../configs/analysis_config.json
# cp ../configs/mut_num_01.json ../configs/analysis_config.json
# cp ../configs/mut_num_02.json ../configs/analysis_config.json

# ******************************************

# # 3. analyze rate of buggy line being selectd as one of the top 50% sbfl ranked lines
# python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 3
# python3 analyzer.py --subject libxml2_TF_top30 --experiment-name TF_top30 --analysis-criteria 3
# python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 3
# python3 analyzer.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --analysis-criteria 3
# python3 analyzer.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --analysis-criteria 3
# python3 analyzer.py --subject opencv_calib3d_TF_top30 --experiment-name TF_top30 --analysis-criteria 3


# # 4. analyze the sbfl rank: naish2
# python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 4
# python3 analyzer.py --subject libxml2_TF_top30 --experiment-name TF_top30 --analysis-criteria 4
# python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 4
# python3 analyzer.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --analysis-criteria 4
# python3 analyzer.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --analysis-criteria 4
# python3 analyzer.py --subject opencv_calib3d_TF_top30 --experiment-name TF_top30 --analysis-criteria 4

# 5. analyze mbfl rank accuracy and mbfl feature extraction time as a whole
# python3 analyzer.py --subject all --experiment-name all --analysis-criteria 6


# 6. analyze the number of mutation utilized as a whole
# "allfails-noReduced-excludeCCT-noHeuristics",
# "rand50-noReduced-excludeCCT-noHeuristics",
# "sbflnaish250-noReduced-excludeCCT-noHeuristics",
# "sbflnaish250-reduced-excludeCCT-noHeuristics",
# "sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics",
# echo "\n\n ** zlib_ng_TF_top30 **"
# python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --type-name allfails-noReduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --type-name rand50-noReduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --type-name sbflnaish250-noReduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --type-name sbflnaish250-reduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --type-name sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"

# echo "\n\n ** libxml2_TF_top30 **"
# python3 analyzer.py --subject libxml2_TF_top30 --experiment-name TF_top30 --type-name allfails-noReduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject libxml2_TF_top30 --experiment-name TF_top30 --type-name rand50-noReduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject libxml2_TF_top30 --experiment-name TF_top30 --type-name sbflnaish250-noReduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject libxml2_TF_top30 --experiment-name TF_top30 --type-name sbflnaish250-reduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject libxml2_TF_top30 --experiment-name TF_top30 --type-name sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"

# echo "\n\n ** opencv_features2d_TF_top30 **"
# python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --type-name allfails-noReduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --type-name rand50-noReduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --type-name sbflnaish250-noReduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --type-name sbflnaish250-reduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --type-name sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"

# echo "\n\n ** opencv_imgproc_TF_top30 **"
# python3 analyzer.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --type-name allfails-noReduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --type-name rand50-noReduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --type-name sbflnaish250-noReduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --type-name sbflnaish250-reduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --type-name sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"

# echo "\n\n ** opencv_core_TF_top30 **"
# python3 analyzer.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --type-name allfails-noReduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --type-name rand50-noReduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --type-name sbflnaish250-noReduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --type-name sbflnaish250-reduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --type-name sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"

# echo "\n\n ** opencv_calib3d_TF_top30 **"
# python3 analyzer.py --subject opencv_calib3d_TF_top30 --experiment-name TF_top30 --type-name allfails-noReduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject opencv_calib3d_TF_top30 --experiment-name TF_top30 --type-name rand50-noReduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject opencv_calib3d_TF_top30 --experiment-name TF_top30 --type-name sbflnaish250-noReduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject opencv_calib3d_TF_top30 --experiment-name TF_top30 --type-name sbflnaish250-reduced-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"
# python3 analyzer.py --subject opencv_calib3d_TF_top30 --experiment-name TF_top30 --type-name sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics --analysis-criteria 7
# echo "========================================"




# ================== machine learning ==================

# zlib_ng-M0 **************************************************************************************
# time python3 machine_learning.py \
#     --subject zlib_ng_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-noReduced-excludeCCT-noHeuristics \
#     --project-name allfails-noReduced-excludeCCT-noHeuristics-ls1 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 20 \
#     --batch-size 128 \
#     --device cuda \
#     --dropout 0.2 \
#     --model-shape 36 64 32 1

# time python3 machine_learning.py \
#     --subject zlib_ng_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-noReduced-excludeCCT-noHeuristics \
#     --inference-name self \
#     --inference \
#     --model-name zlib_ng_TF_top30::allfails-noReduced-excludeCCT-noHeuristics-ls1 \
#     --device cuda

# time python3 machine_learning.py \
#     --subject opencv_calib3d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-noReduced-excludeCCT-noHeuristics \
#     --inference-name opencv_calib3d-D0 \
#     --inference \
#     --model-name zlib_ng_TF_top30::allfails-noReduced-excludeCCT-noHeuristics-ls1 \
#     --device cuda


# zlib_ng-M1
# time python3 machine_learning.py \
#     --subject zlib_ng_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name rand50-noReduced-excludeCCT-noHeuristics \
#     --project-name rand50-noReduced-excludeCCT-noHeuristics-ls1 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 20 \
#     --batch-size 128 \
#     --device cuda \
#     --dropout 0.2 \
#     --model-shape 36 64 32 1

# time python3 machine_learning.py \
#     --subject zlib_ng_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name rand50-noReduced-excludeCCT-noHeuristics \
#     --inference-name self \
#     --inference \
#     --model-name zlib_ng_TF_top30::rand50-noReduced-excludeCCT-noHeuristics-ls1 \
#     --device cuda

# time python3 machine_learning.py \
#     --subject opencv_calib3d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-noReduced-excludeCCT-noHeuristics \
#     --inference-name opencv_calib3d-D0 \
#     --inference \
#     --model-name zlib_ng_TF_top30::rand50-noReduced-excludeCCT-noHeuristics-ls1 \
#     --device cuda


# zlib_ng-M2
# time python3 machine_learning.py \
#     --subject zlib_ng_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name sbflnaish250-noReduced-excludeCCT-noHeuristics \
#     --project-name sbflnaish250-noReduced-excludeCCT-noHeuristics-ls1 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 20 \
#     --batch-size 128 \
#     --device cuda \
#     --dropout 0.2 \
#     --model-shape 36 64 32 1

# time python3 machine_learning.py \
#     --subject zlib_ng_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name sbflnaish250-noReduced-excludeCCT-noHeuristics \
#     --inference-name self \
#     --inference \
#     --model-name zlib_ng_TF_top30::sbflnaish250-noReduced-excludeCCT-noHeuristics-ls1 \
#     --device cuda

# time python3 machine_learning.py \
#     --subject opencv_calib3d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-noReduced-excludeCCT-noHeuristics \
#     --inference-name opencv_calib3d-D0 \
#     --inference \
#     --model-name zlib_ng_TF_top30::sbflnaish250-noReduced-excludeCCT-noHeuristics-ls1 \
#     --device cuda





# libxml2-M0 **************************************************************************************
# time python3 machine_learning.py \
#     --subject libxml2_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-noReduced-excludeCCT-noHeuristics \
#     --project-name allfails-noReduced-excludeCCT-noHeuristics-ls1 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 10 \
#     --batch-size 1024 \
#     --device cuda \
#     --dropout 0.2 \
#     --model-shape 36 64 128 64 32 1
    # here

# time python3 machine_learning.py \
#     --subject libxml2_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-noReduced-excludeCCT-noHeuristics \
#     --inference-name self \
#     --inference \
#     --model-name libxml2_TF_top30::allfails-noReduced-excludeCCT-noHeuristics-ls1 \
#     --device cuda

# time python3 machine_learning.py \
#     --subject opencv_calib3d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-noReduced-excludeCCT-noHeuristics \
#     --inference-name opencv_calib3d-D0 \
#     --inference \
#     --model-name libxml2_TF_top30::allfails-noReduced-excludeCCT-noHeuristics-ls1 \
#     --device cuda


# libxml2-M1
# time python3 machine_learning.py \
#     --subject libxml2_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name rand50-excludeCCT-noHeuristics \
#     --project-name rand50-excludeCCT-noHeuristics-t1 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 10 \
#     --batch-size 1024 \
#     --device cuda \
#     --dropout 0.5 \
#     --model-shape 36 64 128 64 32 1

# time python3 machine_learning.py \
#     --subject libxml2_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name rand50-excludeCCT-noHeuristics \
#     --inference-name self \
#     --inference \
#     --model-name libxml2_TF_top30::rand50-excludeCCT-noHeuristics-t1 \
#     --device cuda

# time python3 machine_learning.py \
#     --subject opencv_calib3d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-excludeCCT-noHeuristics \
#     --inference-name opencv_calib3d-D0 \
#     --inference \
#     --model-name libxml2_TF_top30::rand50-excludeCCT-noHeuristics-t1 \
#     --device cuda


# libxml2-M2
# time python3 machine_learning.py \
#     --subject libxml2_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name sbflnaish250-excludeCCT-noHeuristics \
#     --project-name sbflnaish250-excludeCCT-noHeuristics-t1 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 10 \
#     --batch-size 1024 \
#     --device cuda \
#     --dropout 0.5 \
#     --model-shape 36 64 128 64 32 1

# time python3 machine_learning.py \
#     --subject libxml2_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name sbflnaish250-excludeCCT-noHeuristics \
#     --inference-name self \
#     --inference \
#     --model-name libxml2_TF_top30::sbflnaish250-excludeCCT-noHeuristics-t1 \
#     --device cuda

# time python3 machine_learning.py \
#     --subject opencv_calib3d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-excludeCCT-noHeuristics \
#     --inference-name opencv_calib3d-D0 \
#     --inference \
#     --model-name libxml2_TF_top30::sbflnaish250-excludeCCT-noHeuristics-t1 \
#     --device cuda


# opencv_features2d-M0 **************************************************************************************
# time python3 machine_learning.py \
#     --subject opencv_features2d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-excludeCCT-noHeuristics \
#     --project-name allfails-excludeCCT-noHeuristics-t1 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 10 \
#     --batch-size 512 \
#     --device cuda \
#     --dropout 0.2 \
#     --model-shape 36 64 128 64 32 1

# time python3 machine_learning.py \
#     --subject opencv_features2d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-excludeCCT-noHeuristics \
#     --inference-name self \
#     --inference \
#     --model-name opencv_features2d_TF_top30::allfails-excludeCCT-noHeuristics-t1 \
#     --device cuda

# time python3 machine_learning.py \
#     --subject opencv_calib3d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-excludeCCT-noHeuristics \
#     --inference-name opencv_calib3d-D0 \
#     --inference \
#     --model-name opencv_features2d_TF_top30::allfails-excludeCCT-noHeuristics-t1 \
#     --device cuda


# opencv_features2d-M1
# time python3 machine_learning.py \
#     --subject opencv_features2d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name rand50-excludeCCT-noHeuristics \
#     --project-name rand50-excludeCCT-noHeuristics-t3 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 10 \
#     --batch-size 512 \
#     --device cuda \
#     --dropout 0.2 \
#     --model-shape 36 64 32 1

# time python3 machine_learning.py \
#     --subject opencv_features2d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name rand50-excludeCCT-noHeuristics \
#     --inference-name self \
#     --inference \
#     --model-name opencv_features2d_TF_top30::rand50-excludeCCT-noHeuristics-t1 \
#     --device cuda

# time python3 machine_learning.py \
#     --subject opencv_calib3d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-excludeCCT-noHeuristics \
#     --inference-name opencv_calib3d-D0 \
#     --inference \
#     --model-name opencv_features2d_TF_top30::rand50-excludeCCT-noHeuristics-t1 \
    # --device cuda


# opencv_features2d-M2
# time python3 machine_learning.py \
#     --subject opencv_features2d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name sbflnaish250-excludeCCT-noHeuristics \
#     --project-name sbflnaish250-excludeCCT-noHeuristics-t1 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 10 \
#     --batch-size 512 \
#     --device cuda \
#     --dropout 0.2 \
#     --model-shape 36 64 128 64 32 1

# time python3 machine_learning.py \
#     --subject opencv_features2d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name sbflnaish250-excludeCCT-noHeuristics \
#     --inference-name self \
#     --inference \
#     --model-name opencv_features2d_TF_top30::sbflnaish250-excludeCCT-noHeuristics-t1 \
#     --device cuda

# time python3 machine_learning.py \
#     --subject opencv_calib3d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-excludeCCT-noHeuristics \
#     --inference-name opencv_calib3d-D0 \
#     --inference \
#     --model-name opencv_features2d_TF_top30::sbflnaish250-excludeCCT-noHeuristics-t1 \
#     --device cuda






# opencv_imgproc-M0 **************************************************************************************
# time python3 machine_learning.py \
#     --subject opencv_imgproc_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-excludeCCT-noHeuristics \
#     --project-name allfails-excludeCCT-noHeuristics-t2 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 20 \
#     --batch-size 512 \
#     --device cuda \
#     --dropout 0.5 \
#     --model-shape 36 64 128 64 32 1

# time python3 machine_learning.py \
#     --subject opencv_imgproc_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-excludeCCT-noHeuristics \
#     --inference-name self \
#     --inference \
#     --model-name opencv_imgproc_TF_top30::allfails-excludeCCT-noHeuristics-t2 \
#     --device cuda

# time python3 machine_learning.py \
#     --subject opencv_calib3d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-excludeCCT-noHeuristics \
#     --inference-name opencv_calib3d-D0 \
#     --inference \
#     --model-name opencv_imgproc_TF_top30::allfails-excludeCCT-noHeuristics-t2 \
#     --device cuda


# opencv_imgproc-M1
# time python3 machine_learning.py \
#     --subject opencv_imgproc_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name rand50-excludeCCT-noHeuristics \
#     --project-name rand50-excludeCCT-noHeuristics-t3 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 20 \
#     --batch-size 512 \
#     --device cuda \
#     --dropout 0.5 \
#     --model-shape 36 64 128 64 32 1

# time python3 machine_learning.py \
#     --subject opencv_imgproc_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name rand50-excludeCCT-noHeuristics \
#     --inference-name self \
#     --inference \
#     --model-name opencv_imgproc_TF_top30::rand50-excludeCCT-noHeuristics-t3 \
#     --device cuda

# time python3 machine_learning.py \
#     --subject opencv_calib3d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-excludeCCT-noHeuristics \
#     --inference-name opencv_calib3d-D0 \
#     --inference \
#     --model-name opencv_imgproc_TF_top30::rand50-excludeCCT-noHeuristics-t3 \
#     --device cuda


# opencv_imgproc-M2 
# time python3 machine_learning.py \
#     --subject opencv_imgproc_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name sbflnaish250-excludeCCT-noHeuristics \
#     --project-name sbflnaish250-excludeCCT-noHeuristics-t5 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 20 \
#     --batch-size 512 \
#     --device cuda \
#     --dropout 0.5 \
#     --model-shape 36 64 128 64 32 1

# time python3 machine_learning.py \
#     --subject opencv_imgproc_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name sbflnaish250-excludeCCT-noHeuristics \
#     --inference-name self \
#     --inference \
#     --model-name opencv_imgproc_TF_top30::sbflnaish250-excludeCCT-noHeuristics-t5 \
#     --device cuda

# time python3 machine_learning.py \
#     --subject opencv_calib3d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-excludeCCT-noHeuristics \
#     --inference-name opencv_calib3d-D0 \
#     --inference \
#     --model-name opencv_imgproc_TF_top30::sbflnaish250-excludeCCT-noHeuristics-t5 \
#     --device cuda



# opencv_core-M0 **************************************************************************************
# time python3 machine_learning.py \
#     --subject opencv_core_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-excludeCCT-noHeuristics \
#     --project-name allfails-excludeCCT-noHeuristics-t6 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 10 \
#     --batch-size 512 \
#     --device cuda \
#     --dropout 0.2 \
#     --model-shape 36 64 128 128 64 32 1

# time python3 machine_learning.py \
#     --subject opencv_core_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-excludeCCT-noHeuristics \
#     --inference-name self \
#     --inference \
#     --model-name opencv_core_TF_top30::allfails-excludeCCT-noHeuristics-t6 \
#     --device cuda

# time python3 machine_learning.py \
#     --subject opencv_calib3d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-excludeCCT-noHeuristics \
#     --inference-name opencv_calib3d-D0 \
#     --inference \
#     --model-name opencv_core_TF_top30::allfails-excludeCCT-noHeuristics-t6 \
#     --device cuda


# opencv_core-M1
# time python3 machine_learning.py \
#     --subject opencv_core_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name rand50-excludeCCT-noHeuristics \
#     --project-name rand50-excludeCCT-noHeuristics-t1 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 10 \
#     --batch-size 512 \
#     --device cuda \
#     --dropout 0.2 \
#     --model-shape 36 64 128 128 64 32 1

# time python3 machine_learning.py \
#     --subject opencv_core_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name rand50-excludeCCT-noHeuristics \
#     --inference-name self \
#     --inference \
#     --model-name opencv_core_TF_top30::rand50-excludeCCT-noHeuristics-t1 \
#     --device cuda

# time python3 machine_learning.py \
#     --subject opencv_calib3d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-excludeCCT-noHeuristics \
#     --inference-name opencv_calib3d-D0 \
#     --inference \
#     --model-name opencv_core_TF_top30::rand50-excludeCCT-noHeuristics-t1 \
#     --device cuda


# opencv_core-M2
# time python3 machine_learning.py \
#     --subject opencv_core_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name sbflnaish250-excludeCCT-noHeuristics \
#     --project-name sbflnaish250-excludeCCT-noHeuristics-t1 \
#     --train \
#     --train-validate-test-ratio 8 1 1 \
#     --random-seed 42 \
#     --epoch 10 \
#     --batch-size 512 \
#     --device cuda \
#     --dropout 0.2 \
#     --model-shape 36 64 128 128 64 32 1

# time python3 machine_learning.py \
#     --subject opencv_core_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name sbflnaish250-excludeCCT-noHeuristics \
#     --inference-name self \
#     --inference \
#     --model-name opencv_core_TF_top30::sbflnaish250-excludeCCT-noHeuristics-t1 \
#     --device cuda

# time python3 machine_learning.py \
#     --subject opencv_calib3d_TF_top30 \
#     --experiment-name TF_top30 \
#     --targeting-experiment-name allfails-excludeCCT-noHeuristics \
#     --inference-name opencv_calib3d-D0 \
#     --inference \
#     --model-name opencv_core_TF_top30::sbflnaish250-excludeCCT-noHeuristics-t1 \
#     --device cuda
