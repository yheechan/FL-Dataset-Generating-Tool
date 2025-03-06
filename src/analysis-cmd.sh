# 1. analyze the statiscis of mbfl versions
# python3 analyzer.py --subject opencv_features2d_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject libxml2_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject opencv_imgproc_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject opencv_core_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject opencv_calib3d_TF_top30 --experiment-name TF_top30 --analysis-criteria 1


# ================== FL analysis ==================


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
# python3 analyzer.py --subject all --experiment-name all --analysis-criteria 6 --> which is deprecated

# record the number of mutation utilized as a whole
# python3 analyzer.py --subject all --experiment-name all --analysis-criteria 7

