# time python3 collect_buggy_mutants.py --subject NSFW_c_msg

# time python3 select_usable_versions.py --subject NSFW_c_msg
# python3 validator.py --subject NSFW_c_msg --set-name usable_buggy_versions --validate-usable-buggy-versions

# time python3 prepare_prerequisites.py --subject NSFW_c_msg --target-set-name usable_buggy_versions --exclude-ccts ##~~ --use-excluded-failing-tcs --exclude-ccts --passing-tcs-perc 0.05 --failing-tcs-perc 0.1
# change name according to prerequisite options
# python3 validator.py --subject NSFW_c_msg --set-name prerequisite_data-excluded-CCT-<N>-og --validate-prerequisite-data
# python3 analyzer.py --subject NSFW_c_msg --set-name prerequisite_data-excluded-CCT-<N>-og --output-csv prerequisite_data-excluded-CCT-<N>-og-tc-stats --prerequisite-data --removed-initialization-coverage
# python3 analyzer.py --subject NSFW_c_msg --set-name crashed_buggy_mutants --output crashed_buggy_mutants --crashed-buggy-mutants

# time python3 extract_mbfl_features.py --subject NSFW_c_msg --target-set-name prerequisite_data-excluded-CCT-<N>-og --trial trial1 --exclude-init-lines --parallel-cnt 2 --dont-terminate-leftovers [--remain-one-bug-per-line]
# change name according to prerequisite options
# python3 validator.py --subject NSFW_c_msg --set-name mbfl_features-excluded-CCT-<N>-og --validate-mbfl-features --trial <trial-name>
# python3 ranker.py --subject NSFW_c_msg --set-name mbfl_features-excluded-CCT-<N>-og --output-csv mbfl_features-excluded-CCT-<N>-og-rank-stats --mbfl-features --trial <trial-name>
# python3 analyzer.py --subject NSFW_c_msg --set-name mbfl_features-excluded-CCT-<N>-og --output-csv mbfl_features-excluded-CCT-<N>-og-tc-stats --prerequisite-data --removed-initialization-coverage

# python3 reconstructor.py --subject NSFW_c_msg --set-name mbfl_features-excluded-CCT-34-og --remove-versions-mbfl criteriaA
# python3 validator.py --subject NSFW_c_msg --set-name mbfl_features-excluded-CCT-34-og-removed-criteriaA --validate-mbfl-features --trial <trial-name>
# python3 ranker.py --subject NSFW_c_msg --set-name mbfl_features-excluded-CCT-34-og-removed-criteriaA --output-csv mbfl_features-excluded-CCT-34-og-removed-criteriaA-rank-stats --mbfl-features
# python3 analyzer.py --subject NSFW_c_msg --set-name mbfl_features-excluded-CCT-34-og-removed-criteriaA --output-csv mbfl_features-excluded-CCT-34-og-removed-criteriaA-TC-stats --prerequisite-data --removed-initialization-coverage

# time python3 extract_mbfl_features.py --subject NSFW_c_frw --target-set-name mbfl_features-test-trial1 --trial trial2 --past-trials trial1
# python3 reconstructor.py --subject NSFW_c_frw --set-name mbfl_features-48-test-reconstruction --combine-mbfl-trials --past-trials trial1 trial2

# time python3 extract_sbfl_features.py --subject NSFW_c_msg --target-set-name mbfl_features
# change name according to mbfl_feaeture-<option>-<n>-<type>
# python3 validator.py --subject NSFW_c_msg --set-name sbfl_features-excluded-CCT-28-og --validate-sbfl-features
# python3 ranker.py --subject NSFW_c_msg --set-name sbfl_features-excluded-CCT-28-og --output-csv sbfl_features-excluded-CCT-28-og-rank-stats --sbfl-features

# time python3 extract_sbfl_features.py --subject NSFW_c_msg --target-set-name mbfl_features-excluded-CCT-24-og-removed-criteriaA
# change name according to mbfl_feaeture-<option>-<n>-<type>
# python3 validator.py --subject NSFW_c_msg --set-name sbfl_features-excluded-CCT-24-og-removed-criteriaA --validate-sbfl-features
# python3 ranker.py --subject NSFW_c_msg --set-name sbfl_features-excluded-CCT-24-og-removed-criteriaA --output-csv sbfl_features-excluded-CCT-24-og-removed-criteriaA-rank-stats --sbfl-features

# python3 reconstructor.py --subject NSFW_c_msg --set-name sbfl_features --combine-mbfl-sbfl --combining-trials trial1
# python3 validator.py --subject NSFW_c_msg --set-name FL-dataset-NSFW_c_msg --validate-fl-features

# python3 machine_learning.py --subject2setname-pair NSFW_cpp:FL-dataset-NSFW_cpp --postprocess-fl-features
# python3 machine_learning.py --subject2setname-pair NSFW_cpp:FL-dataset-NSFW_cpp --train --project-name ML-240819-NSFW_cpp-v1 --train-validate-test-ratio 6 1 3 --random-seed 42 --epoch 20 --batch-size 1024 --learning-rate 0.001 --dropout 0.2 --model-shape 35 64 32 1
# python3 machine_learning.py --subject2setname-pair NSFW_cpp:FL-dataset-NSFW_cpp --inference --project-name ML-240819-NSFW_cpp-v1 --inference-name infer-NSFW_cpp-v1

# python3 machine_learning.py --subject2setname-pair NSFW_c:FL-dataset-NSFW_c --postprocess-fl-features
# python3 machine_learning.py --subject2setname-pair NSFW_c:FL-dataset-NSFW_c --train --project-name ML-240819-NSFW_c-v1 --train-validate-test-ratio 6 1 3 --random-seed 42 --epoch 20 --batch-size 1024 --learning-rate 0.001 --dropout 0.2 --model-shape 35 64 32 1
# python3 machine_learning.py --subject2setname-pair NSFW_c:FL-dataset-NSFW_c --inference --project-name ML-240819-NSFW_c-v1 --inference-name infer-NSFW_c-v1
