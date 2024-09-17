date > stage01_start.txt
time python3 collect_buggy_mutants.py --subject opencv_dnn
date > stage01_end.txt

date > stage02_start.txt
time python3 select_usable_versions.py --subject opencv_dnn
date > stage02_end.txt

date > stage03_start.txt
time python3 prepare_prerequisites.py --subject opencv_dnn --target-set-name usable_buggy_versions --exclude-ccts
date > stage03_end.txt
