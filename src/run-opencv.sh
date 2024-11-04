##############
### opencv_dnn
##############

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

python3 validator.py --subject opencv_dnn --set-name mbfl_features_removed_30 --validate-mbfl-features --trial trial1
time python3 ranker.py --subject opencv_dnn --set-name mbfl_features_removed_30 --output-csv mbfl_features_removed_30-rank-stats --mbfl-features --trial trial1 --no-ccts
python3 analyzer.py --subject opencv_dnn --set-name mbfl_features_removed_30 --output-csv mbfl_features_removed_30-tc-stats --prerequisite-data --removed-initialization-coverage

# date > stage05_start-remote.txt
# time python3 extract_sbfl_features.py --subject opencv_dnn --target-set-name mbfl_features_removed_30
# date > stage05_end-remote.txt

python3 validator.py --subject opencv_dnn --set-name sbfl_features --validate-sbfl-features
time python3 ranker.py --subject opencv_dnn --set-name sbfl_features --output-csv sbfl_features-rank-stats --sbfl-features --no-ccts

# python3 reconstructor.py --subject opencv_dnn --set-name sbfl_features --combine-mbfl-sbfl --combining-trials trial1 --no-ccts --done-remotely
# time python3 validator.py --subject opencv_dnn --set-name FL-dataset-opencv_dnn --validate-fl-features



##############
### opencv_core
##############

# date > ../out/opencv_core_execution_timestamp/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject opencv_core
# date > ../out/opencv_core_execution_timestamp/stage01_end-remote.txt

# date > ../out/opencv_core_execution_timestamp/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject opencv_core
# date > ../out/opencv_core_execution_timestamp/stage02_end-remote.txt

# date > ../out/opencv_core_execution_timestamp/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject opencv_core --target-set-name usable_buggy_versions
# date > ../out/opencv_core_execution_timestamp/stage03_end-remote.txt

# date > ../out/opencv_core_execution_timestamp/stage04_start-remote.txt
# time python3 extract_mbfl_features.py --subject opencv_core --target-set-name prerequisite_data --trial trial1 --parallel-cnt 3 --dont-terminate-leftovers
# date > ../out/opencv_core_execution_timestamp/stage04_end-remote.txt

python3 validator.py --subject opencv_core --set-name mbfl_features --validate-mbfl-features --trial trial1
time python3 ranker.py --subject opencv_core --set-name mbfl_features --output-csv mbfl_features-rank-stats --mbfl-features --trial trial1 --no-ccts
python3 analyzer.py --subject opencv_core --set-name mbfl_features --output-csv mbfl_features-tc-stats --prerequisite-data --removed-initialization-coverage

# date > ../out/opencv_core_execution_timestamp/stage05_start-remote.txt
# time python3 extract_sbfl_features.py --subject opencv_core --target-set-name mbfl_features
# date > ../out/opencv_core_execution_timestamp/stage05_end-remote.txt

python3 validator.py --subject opencv_core --set-name sbfl_features --validate-sbfl-features
time python3 ranker.py --subject opencv_core --set-name sbfl_features --output-csv sbfl_features-rank-stats --sbfl-features --no-ccts

# python3 reconstructor.py --subject opencv_core --set-name sbfl_features --combine-mbfl-sbfl --combining-trials trial1 --no-ccts --done-remotely
# time python3 validator.py --subject opencv_core --set-name FL-dataset-opencv_core --validate-fl-features



##############
### opencv_imgproc
##############

# date > ../out/opencv_imgproc_execution_timestamp/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject opencv_imgproc
# date > ../out/opencv_imgproc_execution_timestamp/stage01_end-remote.txt

# date > ../out/opencv_imgproc_execution_timestamp/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject opencv_imgproc
# date > ../out/opencv_imgproc_execution_timestamp/stage02_end-remote.txt

# date > ../out/opencv_imgproc_execution_timestamp/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject opencv_imgproc --target-set-name usable_buggy_versions
# date > ../out/opencv_imgproc_execution_timestamp/stage03_end-remote.txt

# date > ../out/opencv_imgproc_execution_timestamp/stage04_start-remote.txt
# time python3 extract_mbfl_features.py --subject opencv_imgproc --target-set-name prerequisite_data --trial trial1 --parallel-cnt 3 --dont-terminate-leftovers
# date > ../out/opencv_imgproc_execution_timestamp/stage04_end-remote.txt

python3 validator.py --subject opencv_imgproc --set-name mbfl_features_removed_30 --validate-mbfl-features --trial trial1
time python3 ranker.py --subject opencv_imgproc --set-name mbfl_features_removed_30 --output-csv mbfl_features_removed_30-rank-stats --mbfl-features --trial trial1 --no-ccts
python3 analyzer.py --subject opencv_imgproc --set-name mbfl_features_removed_30 --output-csv mbfl_features_removed_30-tc-stats --prerequisite-data --removed-initialization-coverage

# date > ../out/opencv_imgproc_execution_timestamp/stage05_start-remote.txt
# time python3 extract_sbfl_features.py --subject opencv_imgproc --target-set-name mbfl_features_removed_30
# date > ../out/opencv_imgproc_execution_timestamp/stage05_end-remote.txt

python3 validator.py --subject opencv_imgproc --set-name sbfl_features --validate-sbfl-features
time python3 ranker.py --subject opencv_imgproc --set-name sbfl_features --output-csv sbfl_features-rank-stats --sbfl-features --no-ccts

# python3 reconstructor.py --subject opencv_imgproc --set-name sbfl_features --combine-mbfl-sbfl --combining-trials trial1 --no-ccts --done-remotely
# time python3 validator.py --subject opencv_imgproc --set-name FL-dataset-opencv_imgproc --validate-fl-features





##############
### opencv_calib3d
##############

# date > ../out/opencv_calib3d_execution_timestamp/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject opencv_calib3d
# date > ../out/opencv_calib3d_execution_timestamp/stage01_end-remote.txt

# date > ../out/opencv_calib3d_execution_timestamp/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject opencv_calib3d
# date > ../out/opencv_calib3d_execution_timestamp/stage02_end-remote.txt

# date > ../out/opencv_calib3d_execution_timestamp/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject opencv_calib3d --target-set-name usable_buggy_versions
# date > ../out/opencv_calib3d_execution_timestamp/stage03_end-remote.txt

# date > ../out/opencv_calib3d_execution_timestamp/stage04_start-remote.txt
# time python3 extract_mbfl_features.py --subject opencv_calib3d --target-set-name prerequisite_data --trial trial1 --parallel-cnt 3 --dont-terminate-leftovers
# date > ../out/opencv_calib3d_execution_timestamp/stage04_end-remote.txt

python3 validator.py --subject opencv_calib3d --set-name mbfl_features --validate-mbfl-features --trial trial1
time python3 ranker.py --subject opencv_calib3d --set-name mbfl_features_removed_30 --output-csv mbfl_features_removed_30-rank-stats --mbfl-features --trial trial1 --no-ccts
python3 analyzer.py --subject opencv_calib3d --set-name mbfl_features_removed_30 --output-csv mbfl_features_removed_30-tc-stats --prerequisite-data --removed-initialization-coverage

# date > ../out/opencv_calib3d_execution_timestamp/stage05_start-remote.txt
# time python3 extract_sbfl_features.py --subject opencv_calib3d --target-set-name mbfl_features_removed_30
# date > ../out/opencv_calib3d_execution_timestamp/stage05_end-remote.txt

python3 validator.py --subject opencv_calib3d --set-name sbfl_features --validate-sbfl-features
time python3 ranker.py --subject opencv_calib3d --set-name sbfl_features --output-csv sbfl_features-rank-stats --sbfl-features --no-ccts

# python3 reconstructor.py --subject opencv_calib3d --set-name sbfl_features --combine-mbfl-sbfl --combining-trials trial1 --no-ccts --done-remotely
# time python3 validator.py --subject opencv_calib3d --set-name FL-dataset-opencv_calib3d --validate-fl-features


##############
### opencv_features2d
##############

# date > ../out/opencv_features2d_execution_timestamp/stage01_start-remote.txt
# time python3 collect_buggy_mutants.py --subject opencv_features2d
# date > ../out/opencv_features2d_execution_timestamp/stage01_end-remote.txt

# date > ../out/opencv_features2d_execution_timestamp/stage02_start-remote.txt
# time python3 select_usable_versions.py --subject opencv_features2d
# date > ../out/opencv_features2d_execution_timestamp/stage02_end-remote.txt

# python3 validator.py --subject opencv_features2d --set-name usable_buggy_versions --validate-usable-buggy-versions

# date > ../out/opencv_features2d_execution_timestamp/stage03_start-remote.txt
# time python3 prepare_prerequisites.py --subject opencv_features2d --target-set-name usable_buggy_versions
# date > ../out/opencv_features2d_execution_timestamp/stage03_end-remote.txt

# python3 validator.py --subject opencv_features2d --set-name prerequisite_data --validate-prerequisite-data

# date > ../out/opencv_features2d_execution_timestamp/stage04_start-remote.txt
# time python3 extract_mbfl_features.py --subject opencv_features2d --target-set-name prerequisite_data --trial trial1 --parallel-cnt 3 --dont-terminate-leftovers
# date > ../out/opencv_features2d_execution_timestamp/stage04_end-remote.txt

python3 validator.py --subject opencv_features2d --set-name mbfl_features --validate-mbfl-features --trial trial1
time python3 ranker.py --subject opencv_features2d --set-name mbfl_features --output-csv mbfl_features-rank-stats --mbfl-features --trial trial1 --no-ccts
python3 analyzer.py --subject opencv_features2d --set-name mbfl_features --output-csv mbfl_features-tc-stats --prerequisite-data --removed-initialization-coverage

# date > ../out/opencv_features2d_execution_timestamp/stage05_start-remote.txt
# time python3 extract_sbfl_features.py --subject opencv_features2d --target-set-name mbfl_features
# date > ../out/opencv_features2d_execution_timestamp/stage05_end-remote.txt

python3 validator.py --subject opencv_features2d --set-name sbfl_features --validate-sbfl-features
time python3 ranker.py --subject opencv_features2d --set-name sbfl_features --output-csv sbfl_features-rank-stats --sbfl-features --no-ccts

# python3 reconstructor.py --subject opencv_features2d --set-name sbfl_features --combine-mbfl-sbfl --combining-trials trial1 --no-ccts --done-remotely
# time python3 validator.py --subject opencv_features2d --set-name FL-dataset-opencv_features2d --validate-fl-features
