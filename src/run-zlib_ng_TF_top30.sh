# 1. Collect buggy mutants
# date > ../timer/zlib_ng_TF_top30/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 > ../timer/zlib_ng_TF_top30/stage01.log
# date > ../timer/zlib_ng_TF_top30/stage01_end-remote.txt


# Number of tasks (assigned-stage01): 1632
# Number of tasks (mutants-stage01): 2692
# Number of tasks (repo): 240
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30

# sec: 403.33572793006897
# min: 6.722262132167816
# hour: 0.11203770220279693

# 1392 buggy mutants

# ===============================


# 2. Select usable versions
# date > ../timer/zlib_ng_TF_top30/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 > ../timer/zlib_ng_TF_top30/stage02.log
# date > ../timer/zlib_ng_TF_top30/stage02_end-remote.txt

# Number of tasks (assigned_works): 240
# Number of tasks (works): 1392
# Number of tasks (repo): 240
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30

# sec: 228.58901977539062
# min: 3.8098169962565103
# hour: 0.0634969499376085

# 761 usable buggy versions



# ===============================


# 3. Prepare prerequisites
# date > ../timer/zlib_ng_TF_top30/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 > ../timer/zlib_ng_TF_top30/stage03.log
# date > ../timer/zlib_ng_TF_top30/stage03_end-remote.txt


# Number of buggy versions: 761
# Number of tasks (assigned_works): 240
# Number of tasks (works): 761
# Number of tasks (repo): 240
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30

# sec: 493.2056710720062
# min: 8.220094517866771
# hour: 0.1370015752977795

# 737 valid prerequisites


# ===============================

# 4. Extract SBFL features

# date > ../timer/zlib_ng_TF_top30/stage04_start-remote.txt
# time python3 extract_sbfl_features.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --target-set-name prerequisite_data > ../timer/zlib_ng_TF_top30/stage04.log
# date > ../timer/zlib_ng_TF_top30/stage04_end-remote.txt

# Number of tasks (assigned_works): 240
# Number of tasks (works): 737
# Number of tasks (repo): 240
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30

# sec: 34.85499882698059
# min: 0.5809166471163432
# hour: 0.009681944118605719

# 737 valid SBFL features


# ===============================

# 5. Extract MBFL features

# date > ../timer/zlib_ng_TF_top30/stage05_start-remote.txt
# time python3 extract_mbfl_features.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --target-set-name prerequisite_data --trial trial1 --parallel-cnt 3 --dont-terminate-leftovers --version-limit 240 --remain-one-bug-per-line > ../timer/zlib_ng_TF_top30/stage05.log
# date > ../timer/zlib_ng_TF_top30/stage05_end-remote.txt

# Number of tasks (assigned_works): 240
# Number of tasks (works): 167
# Number of tasks (repo): 240
# Number of tasks (configurations): 30
# Number of tasks (src): 30
# Number of tasks (tools): 30
# Number of tasks (configurations): 30

# sec: 11392.129829406738
# min: 189.86883049011232
# hour: 3.1644805081685385


# extracted 167 valid MBFL features


# python3 validator.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --validation-criteria 0
# python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 1
# python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name 



# =============================== 50%

# echo "analyzing zlib_ng_TF_top30 allfails-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name allfails-noReduced-excludeCCT-noHeuristics

# echo "analyzing zlib_ng_TF_top30 rand50-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name rand50-noReduced-excludeCCT-noHeuristics


# =============================== 30%

# echo "analyzing zlib_ng_TF_top30 rand30-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name rand30-noReduced-excludeCCT-noHeuristics

# echo "analyzing zlib_ng_TF_top30 sbflnaish230-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish230-noReduced-excludeCCT-noHeuristics

# ===============================

# echo "analyzing zlib_ng_TF_top30 sbflnaish250-noReduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish250-noReduced-excludeCCT-noHeuristics

# echo "analyzing zlib_ng_TF_top30 sbflnaish250-reduced-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish250-reduced-excludeCCT-noHeuristics

# echo "analyzing zlib_ng_TF_top30 sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics"
# time python3 analyzer.py --subject zlib_ng_TF_top30 --experiment-name TF_top30 --analysis-criteria 2 --type-name sbflnaish250-reduced_sbflnaish2-excludeCCT-noHeuristics



# ===============================


time python3 analyzer.py \
    --subject zlib_ng_TF_top30 \
    --experiment-name TF_top30 \
    --analysis-criteria 9 \
    --batch-size 128

# time python3 analyzer.py \
#     --subject zlib_ng_TF_top30 \
#     --experiment-name TF_top30 \
#     --analysis-criteria 8


# time python3 analyzer.py \
#     --subject zlib_ng_TF_top30 \
#     --experiment-name TF_top30 \
#     --analysis-criteria 9 \
#     --batch-size 128
