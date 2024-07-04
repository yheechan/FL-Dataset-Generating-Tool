# time python3 collect_buggy_mutants.py --subject jsoncpp

# time python3 select_usable_versions.py --subject jsoncpp
# python3 validator.py --subject jsoncpp --set-name usable_buggy_versions --validate-usable-buggy-versions

# time python3 prepare_prerequisites.py --subject jsoncpp --target-set-name usable_buggy_versions --use-excluded-failing-tcs --exclude-ccts --passing-tcs-perc 0.05 --failing-tcs-perc 0.1
# python3 validator.py --subject jsoncpp --set-name prerequisite_data --validate-prerequisite-data

# time python3 extract_mbfl_features.py --subject jsoncpp --target-set-name prerequisite_data
# python3 validator.py --subject jsoncpp --set-name mbfl_features --validate-mbfl-features
# python3 ranker.py --subject jsoncpp --set-name mbfl_features --output-csv mbfl_features --mbfl-features

# time python3 extract_sbfl_features.py --subject jsoncpp --target-set-name mbfl_features
# python3 validator.py --subject jsoncpp --set-name sbfl_features --validate-sbfl-features
# python3 ranker.py --subject jsoncpp --set-name sbfl_features --output-csv sbfl_features --sbfl-features

# python3 reconstructor.py --subject jsoncpp --set-name sbfl_features --combine-mbfl-sbfl
# python3 validator.py --subject jsoncpp --set-name FL-dataset-jsoncpp --validate-fl-features
