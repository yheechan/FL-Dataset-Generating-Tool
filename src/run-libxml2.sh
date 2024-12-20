# 1. Collect buggy mutants
# date > ../timer/libxml2/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject libxml2 > ../timer/libxml2/stage01.log
# date > ../timer/libxml2/stage01_end-remote.txt

# Number of tasks (assigned-stage01): 8640
# Number of tasks (mutants-stage01): 171135
# Number of tasks (repo): 264
# Number of tasks (configurations): 33
# Number of tasks (src): 33
# Number of tasks (tools): 33
# Number of tasks (configurations): 33

# Worker finished in:
    # sec: 27135.889765262604
    # min: 452.2648294210434
    # hour: 7.53774715701739

# 38022 buggy mutants


# ===============================


# 2. Select usable versions
# date > ../timer/libxml2/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject libxml2 > ../timer/libxml2/stage02.log
# date > ../timer/libxml2/stage02_end-remote.txt

# Number of tasks (assigned_works): 264
# Number of tasks (works): 4000
# Number of tasks (repo): 264
# Number of tasks (configurations): 33
# Number of tasks (src): 33
# Number of tasks (tools): 33
# Number of tasks (configurations): 33

# Worker finished in:
    # sec: 14511.585643529892
    # min: 241.8597607254982
    # hour: 4.030996012091637

# Number of tasks (assigned_works): 264
# Number of tasks (works): 599
# Number of tasks (repo): 264
# Number of tasks (configurations): 33
# Number of tasks (src): 33
# Number of tasks (tools): 33
# Number of tasks (configurations): 33

# Worker finished in:
    # sec: 13717.155438184738
    # min: 228.61925730307897
    # hour: 3.810320955051316

# time python3 validator.py --subject libxml2 --set-name usable_buggy_versions --validate-usable-buggy-versions

# 3753 usable buggy versions


# ===============================


# 3. Prepare prerequisites
# date > ../timer/libxml2/stage03_start-remote-v1.txt
# time python3 prepare_prerequisites.py --subject libxml2 --target-set-name usable_buggy_versions_v1 > ../timer/libxml2/stage03-v1.log
# date > ../timer/libxml2/stage03_end-remote-v1.txt

# Number of tasks (assigned_works): 248
# Number of tasks (works): 944
# Number of tasks (repo): 248
# Number of tasks (configurations): 31
# Number of tasks (src): 31
# Number of tasks (tools): 31
# Number of tasks (configurations): 31

# Worker finished in:
    # sec: 86277.47780585289
    # min: 1437.9579634308816
    # hour: 23.965966057181358

# 916 retrieved prerequisites


# date > ../timer/libxml2/stage03_start-remote-v2.txt
# time python3 prepare_prerequisites.py --subject libxml2 --target-set-name usable_buggy_versions_v2 > ../timer/libxml2/stage03-v1.log
# date > ../timer/libxml2/stage03_end-remote-v2.txt

# date > ../timer/libxml2/stage03_start-remote-v3.txt
# time python3 prepare_prerequisites.py --subject libxml2 --target-set-name usable_buggy_versions_v3 > ../timer/libxml2/stage03-v1.log
# date > ../timer/libxml2/stage03_end-remote-v3.txt

# date > ../timer/libxml2/stage03_start-remote-v4.txt
# time python3 prepare_prerequisites.py --subject libxml2 --target-set-name usable_buggy_versions_v4 > ../timer/libxml2/stage03-v1.log
# date > ../timer/libxml2/stage03_end-remote-v4.txt

# Number of tasks (assigned_works): 272
# Number of tasks (works): 1179
# Number of tasks (repo): 272
# Number of tasks (configurations): 34
# Number of tasks (src): 34
# Number of tasks (tools): 34
# Number of tasks (configurations): 34

# real    6m39.909s
# user    1m20.045s
# sys     1m1.440s

# 1148 valid prerequisites


# time python3 validator.py --subject libxml2 --set-name prerequisite_data --validate-prerequisite-data
# time python3 analyzer.py --subject libxml2 --set-name prerequisite_data --output-csv prerequisite_data-tc-stats --prerequisite-data --removed-initialization-coverage
