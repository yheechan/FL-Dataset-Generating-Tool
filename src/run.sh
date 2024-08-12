# time python3 collect_buggy_mutants.py --subject NSFW_thread

# time python3 select_usable_versions.py --subject NSFW_thread
# python3 validator.py --subject NSFW_thread --set-name usable_buggy_versions --validate-usable-buggy-versions

# time python3 prepare_prerequisites.py --subject NSFW_thread --target-set-name usable_buggy_versions --use-excluded-failing-tcs --exclude-ccts --passing-tcs-perc 0.05 --failing-tcs-perc 0.1
# change name according to prerequisite options
# python3 validator.py --subject NSFW_thread --set-name prerequisite_data-excluded-CCT-34-og --validate-prerequisite-data
# python3 analyzer.py --subject NSFW_thread --set-name prerequisite_data-excluded-CCT-34-og --output-csv prerequisite_data-excluded-CCT-34-og-tc-stats --prerequisite-data
# python3 analyzer.py --subject NSFW_thread --set-name crashed_buggy_mutants --output crashed_buggy_mutants --crashed-buggy-mutants

# time python3 extract_mbfl_features.py --subject NSFW_thread --target-set-name prerequisite_data-excluded-CCT-34-og
# change name according to prerequisite options
# python3 validator.py --subject NSFW_thread --set-name mbfl_features-excluded-CCT-34-og --validate-mbfl-features --trial <trial-name>
# python3 ranker.py --subject NSFW_thread --set-name mbfl_features-excluded-CCT-34-og --output-csv mbfl_features-excluded-CCT-34-og-rank-stats --mbfl-features
# python3 analyzer.py --subject NSFW_thread --set-name mbfl_features-excluded-CCT-34-og --output-csv mbfl_features-excluded-CCT-34-og-tc-stats --prerequisite-data

# python3 reconstructor.py --subject NSFW_thread --set-name mbfl_features-excluded-CCT-34-og --remove-versions-mbfl criteriaA
# python3 validator.py --subject NSFW_thread --set-name mbfl_features-excluded-CCT-34-og-removed-criteriaA --validate-mbfl-features --trial <trial-name>
# python3 ranker.py --subject NSFW_thread --set-name mbfl_features-excluded-CCT-34-og-removed-criteriaA --output-csv mbfl_features-excluded-CCT-34-og-removed-criteriaA-rank-stats --mbfl-features
# python3 analyzer.py --subject NSFW_thread --set-name mbfl_features-excluded-CCT-34-og-removed-criteriaA --output-csv mbfl_features-excluded-CCT-34-og-removed-criteriaA-TC-stats --prerequisite-data

# time python3 extract_mbfl_features.py --subject NSFW_c_frw --target-set-name mbfl_features-test-trial1 --trial trial2 --past-trials trial1
# python3 reconstructor.py --subject NSFW_c_frw --set-name mbfl_features-48-test-reconstruction --combine-mbfl-trials --past-trials trial1 trial2

# time python3 extract_sbfl_features.py --subject NSFW_thread --target-set-name mbfl_features
# change name according to mbfl_feaeture-<option>-<n>-<type>
# python3 validator.py --subject NSFW_thread --set-name sbfl_features-excluded-CCT-28-og --validate-sbfl-features
# python3 ranker.py --subject NSFW_thread --set-name sbfl_features-excluded-CCT-28-og --output-csv sbfl_features-excluded-CCT-28-og-rank-stats --sbfl-features

# time python3 extract_sbfl_features.py --subject NSFW_thread --target-set-name mbfl_features-excluded-CCT-24-og-removed-criteriaA
# change name according to mbfl_feaeture-<option>-<n>-<type>
# python3 validator.py --subject NSFW_thread --set-name sbfl_features-excluded-CCT-24-og-removed-criteriaA --validate-sbfl-features
# python3 ranker.py --subject NSFW_thread --set-name sbfl_features-excluded-CCT-24-og-removed-criteriaA --output-csv sbfl_features-excluded-CCT-24-og-removed-criteriaA-rank-stats --sbfl-features

# python3 reconstructor.py --subject NSFW_thread --set-name sbfl_features --combine-mbfl-sbfl
# python3 validator.py --subject NSFW_thread --set-name FL-dataset-NSFW_thread --validate-fl-features

# python3 machine_learning.py --subject2setname-pair jsoncpp:fl_dataset-240419-v1 --postprocess-fl-features
# python3 machine_learning.py --subject2setname-pair jsoncpp:fl_dataset-240419-v1 --train --project-name ML-240808-jsoncpp-v1 --train-validate-test-ratio 6 1 3 --epoch 10 --batch-size 1024
# python3 machine_learning.py --subject2setname-pair jsoncpp:fl_dataset-240419-v1 --inference --project-name ML-240808-jsoncpp-v1 --inference-name infer-jsoncpp-v1
