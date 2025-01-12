# 1. analyze the statiscis of mbfl versions
# python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 1
# python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 1


# mbfl results
# cp ../configs/exp1.json ../configs/analysis_config.json
# echo "analyzing opencv_features2d_TF_top30 rand50-excludeCCT-noHeuristics-delibIncl"
# time python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name rand50-excludeCCT-noHeuristics-delibIncl
# echo "analyzing opencv_features2d_TF_bot30 rand50-excludeCCT-noHeuristics-delibIncl"
# time python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name rand50-excludeCCT-noHeuristics-delibIncl
# echo "analyzing zlib_ng_TF_top30 rand50-excludeCCT-noHeuristics-delibIncl"
# time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name rand50-excludeCCT-noHeuristics-delibIncl
# echo "analyzing zlib_ng_TF_bot30 rand50-excludeCCT-noHeuristics-delibIncl"
# time python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name rand50-excludeCCT-noHeuristics-delibIncl

# cp ../configs/exp2.json ../configs/analysis_config.json
# echo "analyzing opencv_features2d_TF_top30 rand50-excludeCCT-noHeuristics-noDelibIncl"
# time python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name rand50-excludeCCT-noHeuristics-noDelibIncl
# echo "analyzing opencv_features2d_TF_bot30 rand50-excludeCCT-noHeuristics-noDelibIncl"
# time python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name rand50-excludeCCT-noHeuristics-noDelibIncl
# echo "analyzing zlib_ng_TF_top30 rand50-excludeCCT-noHeuristics-noDelibIncl"
# time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name rand50-excludeCCT-noHeuristics-noDelibIncl
# echo "analyzing zlib_ng_TF_bot30 rand50-excludeCCT-noHeuristics-noDelibIncl"
# time python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name rand50-excludeCCT-noHeuristics-noDelibIncl

# cp ../configs/exp3.json ../configs/analysis_config.json
# echo "analyzing opencv_features2d_TF_top30 sbflgp13-excludeCCT-noHeuristics-delibIncl"
# time python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflgp13-excludeCCT-noHeuristics-delibIncl
# echo "analyzing opencv_features2d_TF_bot30 sbflgp13-excludeCCT-noHeuristics-delibIncl"
# time python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name sbflgp13-excludeCCT-noHeuristics-delibIncl
# echo "analyzing zlib_ng_TF_top30 sbflgp13-excludeCCT-noHeuristics-delibIncl"
# time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflgp13-excludeCCT-noHeuristics-delibIncl
# echo "analyzing zlib_ng_TF_bot30 sbflgp13-excludeCCT-noHeuristics-delibIncl"
# time python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name sbflgp13-excludeCCT-noHeuristics-delibIncl

# cp ../configs/exp4.json ../configs/analysis_config.json
# echo "analyzing opencv_features2d_TF_top30 sbflgp13-excludeCCT-noHeuristics-noDelibIncl"
# time python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl
# echo "analyzing opencv_features2d_TF_bot30 sbflgp13-excludeCCT-noHeuristics-noDelibIncl"
# time python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl
# echo "analyzing zlib_ng_TF_top30 sbflgp13-excludeCCT-noHeuristics-noDelibIncl"
# time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl
# echo "analyzing zlib_ng_TF_bot30 sbflgp13-excludeCCT-noHeuristics-noDelibIncl"
# time python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl



# 3. analyze rate of buggy line being in the top 30 sbfl ranked lines
# python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 3
# python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 3
# python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 3
# python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 3




# python3 machine_learning.py --prepare-fl-features --subject zlib_ng_TF_bot30 --experiment-name TF_bot30
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --train --project-name test1 --train-validate-test-ratio 6 2 2 --random-seed 42 --epoch 3 --batch-size 12 --device cuda --dropout 0.2 --model-shape 35 512 12 1
# python3 machine_learning.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --inference --model-name zlib_ng_TF_top30-test1 --inference-name 2zlib_ng_TF_bot30test1


# time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name test1
# python3 machine_learning.py --prepare-fl-features --subject zlib_ng_TF_top30 --experiment-name TF_top30 --type-name test1
# python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 3




# train
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name rand50-excludeCCT-noHeuristics-delibIncl
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --train --project-name rand50-excludeCCT-noHeuristics-delibIncl-t6 --train-validate-test-ratio 8 1 1 --epoch 10 --batch-size 256 --device cuda --dropout 0.2 --model-shape 35 64 64 32 1
# infer
# D1 python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --inference --model-name opencv_features2d_TF_top30::rand50-excludeCCT-noHeuristics-delibIncl-t6 --inference-name self-t1
# D5 python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --inference --model-name opencv_features2d_TF_top30::rand50-excludeCCT-noHeuristics-delibIncl-t6 --inference-name zlib_ng_TF_top30_rand50_delibIncl
# D6 python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --inference --model-name opencv_features2d_TF_top30::rand50-excludeCCT-noHeuristics-delibIncl-t6 --inference-name zlib_ng_TF_top30_rand50_noDelibIncl
# D7 python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --inference --model-name opencv_features2d_TF_top30::rand50-excludeCCT-noHeuristics-delibIncl-t6 --inference-name zlib_ng_TF_top30_sbflgp13_delibIncl
# D8 python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --inference --model-name opencv_features2d_TF_top30::rand50-excludeCCT-noHeuristics-delibIncl-t6 --inference-name zlib_ng_TF_top30_sbflgp13_noDelibIncl

# set data
# D5 python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name rand50-excludeCCT-noHeuristics-delibIncl
# D6 python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name rand50-excludeCCT-noHeuristics-noDelibIncl
# D7 python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name sbflgp13-excludeCCT-noHeuristics-delibIncl
# D8 python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl



# train
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name rand50-excludeCCT-noHeuristics-noDelibIncl
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --train --project-name rand50-excludeCCT-noHeuristics-noDelibIncl-t1 --train-validate-test-ratio 8 1 1 --epoch 20 --batch-size 256 --device cuda --dropout 0.2 --model-shape 35 64 64 32 1
# infer
# D2
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --inference --model-name opencv_features2d_TF_top30::rand50-excludeCCT-noHeuristics-noDelibIncl-t1 --inference-name self-t1

# set data and infer and train and infer
# D5
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name rand50-excludeCCT-noHeuristics-delibIncl
# D5
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --inference --model-name opencv_features2d_TF_top30::rand50-excludeCCT-noHeuristics-noDelibIncl-t1 --inference-name zlib_ng_TF_top30_rand50_delibIncl
# D2
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --inference --model-name zlib_ng_TF_top30::rand50-excludeCCT-noHeuristics-delibIncl-t1 --inference-name opencv_features2d_TF_top30_rand50_noDelibIncl

# D6
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name rand50-excludeCCT-noHeuristics-noDelibIncl
# D6
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --inference --model-name opencv_features2d_TF_top30::rand50-excludeCCT-noHeuristics-noDelibIncl-t1 --inference-name zlib_ng_TF_top30_rand50_noDelibIncl
# D2
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --inference --model-name zlib_ng_TF_top30::rand50-excludeCCT-noHeuristics-noDelibIncl-t1 --inference-name opencv_features2d_TF_top30_rand50_noDelibIncl

# D7
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name sbflgp13-excludeCCT-noHeuristics-delibIncl
# D7
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --inference --model-name opencv_features2d_TF_top30::rand50-excludeCCT-noHeuristics-noDelibIncl-t1 --inference-name zlib_ng_TF_top30_sbflgp13_delibIncl
# D2
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --inference --model-name zlib_ng_TF_top30::sbflgp13-excludeCCT-noHeuristics-delibIncl-t1 --inference-name opencv_features2d_TF_top30_rand50_noDelibIncl

# D8
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl
# D8
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --inference --model-name opencv_features2d_TF_top30::rand50-excludeCCT-noHeuristics-noDelibIncl-t1 --inference-name zlib_ng_TF_top30_sbflgp13_noDelibIncl
# D2
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --inference --model-name zlib_ng_TF_top30::sbflgp13-excludeCCT-noHeuristics-noDelibIncl-t1 --inference-name opencv_features2d_TF_top30_rand50_noDelibIncl


# train
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name sbflgp13-excludeCCT-noHeuristics-delibIncl
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --train --project-name sbflgp13-excludeCCT-noHeuristics-delibIncl-t1 --train-validate-test-ratio 8 1 1 --epoch 20 --batch-size 256 --device cuda --dropout 0.2 --model-shape 35 64 64 32 1
# infer
# D3
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --inference --model-name opencv_features2d_TF_top30::sbflgp13-excludeCCT-noHeuristics-delibIncl-t1 --inference-name self-t1

# set data and infer and train and infer
# # D5
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name rand50-excludeCCT-noHeuristics-delibIncl
# # D5
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --inference --model-name opencv_features2d_TF_top30::sbflgp13-excludeCCT-noHeuristics-delibIncl-t1 --inference-name zlib_ng_TF_top30_rand50_delibIncl
# # D3
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --inference --model-name zlib_ng_TF_top30::rand50-excludeCCT-noHeuristics-delibIncl-t1 --inference-name opencv_features2d_TF_top30_sbflgp13_delibIncl

# # D6
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name rand50-excludeCCT-noHeuristics-noDelibIncl
# # D6
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --inference --model-name opencv_features2d_TF_top30::sbflgp13-excludeCCT-noHeuristics-delibIncl-t1 --inference-name zlib_ng_TF_top30_rand50_noDelibIncl
# # D3
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --inference --model-name zlib_ng_TF_top30::rand50-excludeCCT-noHeuristics-noDelibIncl-t1 --inference-name opencv_features2d_TF_top30_sbflgp13_delibIncl

# # D7
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name sbflgp13-excludeCCT-noHeuristics-delibIncl
# # D7
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --inference --model-name opencv_features2d_TF_top30::sbflgp13-excludeCCT-noHeuristics-delibIncl-t1 --inference-name zlib_ng_TF_top30_sbflgp13_delibIncl
# # D3
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --inference --model-name zlib_ng_TF_top30::sbflgp13-excludeCCT-noHeuristics-delibIncl-t1 --inference-name opencv_features2d_TF_top30_sbflgp13_delibIncl

# # D8
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl
# # D8
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --inference --model-name opencv_features2d_TF_top30::sbflgp13-excludeCCT-noHeuristics-delibIncl-t1 --inference-name zlib_ng_TF_top30_sbflgp13_noDelibIncl
# # D3
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --inference --model-name zlib_ng_TF_top30::sbflgp13-excludeCCT-noHeuristics-noDelibIncl-t1 --inference-name opencv_features2d_TF_top30_sbflgp13_delibIncl









# train
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --train --project-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl-t1 --train-validate-test-ratio 8 1 1 --epoch 20 --batch-size 256 --device cuda --dropout 0.2 --model-shape 35 64 64 32 1
# infer
# D4
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --inference --model-name opencv_features2d_TF_top30::sbflgp13-excludeCCT-noHeuristics-noDelibIncl-t1 --inference-name self-t1

# # set data and infer and train and infer
# # D5
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name rand50-excludeCCT-noHeuristics-delibIncl
# # D5
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --inference --model-name opencv_features2d_TF_top30::sbflgp13-excludeCCT-noHeuristics-noDelibIncl-t1 --inference-name zlib_ng_TF_top30_rand50_delibIncl
# # D4
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --inference --model-name zlib_ng_TF_top30::rand50-excludeCCT-noHeuristics-delibIncl-t1 --inference-name opencv_features2d_TF_top30_sbflgp13_noDelibIncl

# # D6
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name rand50-excludeCCT-noHeuristics-noDelibIncl
# # D6
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --inference --model-name opencv_features2d_TF_top30::sbflgp13-excludeCCT-noHeuristics-noDelibIncl-t1 --inference-name zlib_ng_TF_top30_rand50_noDelibIncl
# # D4
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --inference --model-name zlib_ng_TF_top30::rand50-excludeCCT-noHeuristics-noDelibIncl-t1 --inference-name opencv_features2d_TF_top30_sbflgp13_noDelibIncl

# # D7
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name sbflgp13-excludeCCT-noHeuristics-delibIncl
# # D7
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --inference --model-name opencv_features2d_TF_top30::sbflgp13-excludeCCT-noHeuristics-noDelibIncl-t1 --inference-name zlib_ng_TF_top30_sbflgp13_delibIncl
# # D4
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --inference --model-name zlib_ng_TF_top30::sbflgp13-excludeCCT-noHeuristics-delibIncl-t1 --inference-name opencv_features2d_TF_top30_sbflgp13_noDelibIncl

# # D8
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl
# # D8
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --inference --model-name opencv_features2d_TF_top30::sbflgp13-excludeCCT-noHeuristics-noDelibIncl-t1 --inference-name zlib_ng_TF_top30_sbflgp13_noDelibIncl
# # D4
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --inference --model-name zlib_ng_TF_top30::sbflgp13-excludeCCT-noHeuristics-noDelibIncl-t1 --inference-name opencv_features2d_TF_top30_sbflgp13_noDelibIncl






# for zlib_ng_TF_top30
# train
python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name rand50-excludeCCT-noHeuristics-delibIncl
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --train --project-name rand50-excludeCCT-noHeuristics-delibIncl-t1 --train-validate-test-ratio 8 1 1 --epoch 10 --batch-size 512 --device cuda --dropout 0.2 --model-shape 35 64 64 32 1
# infer
# D5 python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --inference --model-name zlib_ng_TF_top30::rand50-excludeCCT-noHeuristics-delibIncl-t1 --inference-name self-t1
# D1 python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --inference --model-name zlib_ng_TF_top30::rand50-excludeCCT-noHeuristics-delibIncl-t1 --inference-name opencv_features2d_TF_top30_rand50_delibIncl



# train
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name rand50-excludeCCT-noHeuristics-noDelibIncl
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --train --project-name rand50-excludeCCT-noHeuristics-noDelibIncl-t1 --train-validate-test-ratio 8 1 1 --epoch 10 --batch-size 512 --device cuda --dropout 0.2 --model-shape 35 64 64 32 1
# infer
# D6
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --inference --model-name zlib_ng_TF_top30::rand50-excludeCCT-noHeuristics-noDelibIncl-t1 --inference-name self-t1
# D1
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --inference --model-name zlib_ng_TF_top30::rand50-excludeCCT-noHeuristics-noDelibIncl-t1 --inference-name opencv_features2d_TF_top30_rand50_noDelibIncl



# train
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name sbflgp13-excludeCCT-noHeuristics-delibIncl
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --train --project-name sbflgp13-excludeCCT-noHeuristics-delibIncl-t1 --train-validate-test-ratio 8 1 1 --epoch 10 --batch-size 512 --device cuda --dropout 0.2 --model-shape 35 64 64 32 1
# infer
# D7
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --inference --model-name zlib_ng_TF_top30::sbflgp13-excludeCCT-noHeuristics-delibIncl-t1 --inference-name self-t1
# D1
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --inference --model-name zlib_ng_TF_top30::sbflgp13-excludeCCT-noHeuristics-delibIncl-t1 --inference-name opencv_features2d_TF_top30_sbflgp13_delibIncl


# train
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --prepare-fl-features --type-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --train --project-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl-t1 --train-validate-test-ratio 8 1 1 --epoch 10 --batch-size 512 --device cuda --dropout 0.2 --model-shape 35 64 64 32 1
# infer
# D8
# python3 machine_learning.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --inference --model-name zlib_ng_TF_top30::sbflgp13-excludeCCT-noHeuristics-noDelibIncl-t1 --inference-name self-t1
# D1
# python3 machine_learning.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --inference --model-name zlib_ng_TF_top30::sbflgp13-excludeCCT-noHeuristics-noDelibIncl-t1 --inference-name opencv_features2d_TF_top30_sbflgp13_noDelibIncl








