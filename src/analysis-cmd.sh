# 1. analyze the statiscis of mbfl versions
# python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 1
# python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 1


# mbfl results
cp ../configs/exp1.json ../configs/analysis_config.json
echo "analyzing opencv_features2d_TF_top30 rand50-excludeCCT-noHeuristics-delibIncl"
time python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name rand50-excludeCCT-noHeuristics-delibIncl
echo "analyzing opencv_features2d_TF_bot30 rand50-excludeCCT-noHeuristics-delibIncl"
time python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name rand50-excludeCCT-noHeuristics-delibIncl
echo "analyzing zlib_ng_TF_top30 rand50-excludeCCT-noHeuristics-delibIncl"
time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name rand50-excludeCCT-noHeuristics-delibIncl
echo "analyzing zlib_ng_TF_bot30 rand50-excludeCCT-noHeuristics-delibIncl"
time python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name rand50-excludeCCT-noHeuristics-delibIncl

cp ../configs/exp2.json ../configs/analysis_config.json
echo "analyzing opencv_features2d_TF_top30 rand50-excludeCCT-noHeuristics-noDelibIncl"
time python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name rand50-excludeCCT-noHeuristics-noDelibIncl
echo "analyzing opencv_features2d_TF_bot30 rand50-excludeCCT-noHeuristics-noDelibIncl"
time python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name rand50-excludeCCT-noHeuristics-noDelibIncl
echo "analyzing zlib_ng_TF_top30 rand50-excludeCCT-noHeuristics-noDelibIncl"
time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name rand50-excludeCCT-noHeuristics-noDelibIncl
echo "analyzing zlib_ng_TF_bot30 rand50-excludeCCT-noHeuristics-noDelibIncl"
time python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name rand50-excludeCCT-noHeuristics-noDelibIncl

cp ../configs/exp3.json ../configs/analysis_config.json
echo "analyzing opencv_features2d_TF_top30 sbflgp13-excludeCCT-noHeuristics-delibIncl"
time python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflgp13-excludeCCT-noHeuristics-delibIncl
echo "analyzing opencv_features2d_TF_bot30 sbflgp13-excludeCCT-noHeuristics-delibIncl"
time python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name sbflgp13-excludeCCT-noHeuristics-delibIncl
echo "analyzing zlib_ng_TF_top30 sbflgp13-excludeCCT-noHeuristics-delibIncl"
time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflgp13-excludeCCT-noHeuristics-delibIncl
echo "analyzing zlib_ng_TF_bot30 sbflgp13-excludeCCT-noHeuristics-delibIncl"
time python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name sbflgp13-excludeCCT-noHeuristics-delibIncl

cp ../configs/exp4.json ../configs/analysis_config.json
echo "analyzing opencv_features2d_TF_top30 sbflgp13-excludeCCT-noHeuristics-noDelibIncl"
time python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl
echo "analyzing opencv_features2d_TF_bot30 sbflgp13-excludeCCT-noHeuristics-noDelibIncl"
time python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl
echo "analyzing zlib_ng_TF_top30 sbflgp13-excludeCCT-noHeuristics-noDelibIncl"
time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl
echo "analyzing zlib_ng_TF_bot30 sbflgp13-excludeCCT-noHeuristics-noDelibIncl"
time python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 2 --type-name sbflgp13-excludeCCT-noHeuristics-noDelibIncl



# 3. analyze rate of buggy line being in the top 30 sbfl ranked lines
# python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 3
# python3 analyzer.py --subject opencv_features2d_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 3
# python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 3
# python3 analyzer.py --subject zlib_ng_TF_bot30 --experiment-name TF_bot30 --analysis-criteria 3


