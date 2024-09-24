# date > stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject opencv_dnn
# date > stage01_end-remote.txt

# date > stage02_start-remote.txt
# time python3 select_usable_versions.py --subject opencv_dnn
# date > stage02_end-remote.txt

# date > stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject opencv_dnn --target-set-name usable_buggy_versions
# date > stage03_end-remote.txt

# date > stage04_start-remote.txt
# time python3 extract_mbfl_features.py --subject opencv_dnn --target-set-name prerequisite_data --trial trial1 --parallel-cnt 3 --dont-terminate-leftovers
# date > stage04_start-remote.txt

date > stage05_start-remote.txt
time python3 extract_sbfl_features.py --subject opencv_dnn --target-set-name mbfl_features_removed_30
date > stage05_end-remote.txt
