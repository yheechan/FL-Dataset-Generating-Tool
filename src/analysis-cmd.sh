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




# ******************************************
# ADD COSINE SIMILARITY OF PASSINGS TCS IN DB
# python3 analyzer.py --subject all --experiment-name all --analysis-criteria 10

# RECORD THE SBFL SCORES FOR EACH DATASET
# python3 analyzer.py --subject all --experiment-name all --analysis-criteria 4

# RECORD UTILIZED DATA (MUT, TCS) INFORMATION FOR EACH DATASET
# python3 analyzer.py --subject all --experiment-name all --analysis-criteria 7

# CONDUCT ML EXPERIMENTS WITH 10 VARIED PARAMETERS
# python3 analyzer.py --subject all --experiment-name all --analysis-criteria X