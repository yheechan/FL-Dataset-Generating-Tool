# time python3 collect_buggy_mutants.py --subject jsoncpp
# time python3 select_usable_versions.py --subject jsoncpp
# time python3 prepare_prerequisites.py --subject jsoncpp --target-set-name usable_buggy_versions --use-excluded-failing-tcs --exclude-ccts --passing-tcs-perc 0.05 --failing-tcs-perc 0.1
# time python3 extract_mbfl_features.py --subject jsoncpp --target-set-name prerequisite_data
# time python3 extract_sbfl_features.py --subject jsoncpp --target-set-name mbfl_features