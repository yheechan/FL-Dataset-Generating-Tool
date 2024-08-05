# Fault Localization Dataset Generator for C/C++ Subjects

## Dependencies
* LLVM 13.0.1
  * link: https://apt.llvm.org/
  * required to install "all" packages of LLVM ($ sudo ./llvm.sh 13 all)

* python 3.8
  * numpy
  * csv
  * json
  * math
  * argparse
  * time
  * multiprocessing
  * subprocess
  * random
  * pathlib
  * os
* gcovr 6.0 (and above)
* bear 2.3.11
* GNU make 4.1
* cmake 3.10.2

* rsync  version 3.1.2  protocol version 31
* diff (GNU diffutils) 3.6
* GNU patch 2.7.6

* VIM - Vi IMproved 8.0
* OpenSSH_7.6p1 Ubuntu-4ubuntu0.7, OpenSSL 1.0.2n
* Visual Studio Code
* tmux 2.6

## Build Step
### 1. Build MUSICUP
```
$ cd tools/MUSICUP/
$ make LLVM_BUILD_PATH=/usr/lib/llvm-13 -j20
```

### 2. Build extractor
```
$ cd tools/extractor/
$ make -j20
```

## FL dataset generating executables
* directory: ``src/``
* list of executables for dataset generation:
  1. ``collect_buggy_mutants.py``                                                                                                  
  2. ``select_usable_versions.py``
  3. ``prepare_prerequisites.py``
  4. ``extract_mbfl_features.py``
  5. ``extract_sbfl_features.py``
  6. ``combine_fl_features.py``
* list of executables for dataset generation on a single version of a subject:
  1. ``test_mutant_buggy_collection.py``: tests a mutant for buggy collections (version saved when considered as buggy)
  2. ``test_version_usability_check.py``: tests a buggy mutant for usability check (version saved when considered as usable)
  3. ``test_version_prerequisites.py``: tests a version (from usable_buggy_versions) in order to extract (prepare) prerequisite data
  4. ``test_version_mbfl_features.py``: tests a version (that includes prerequisite data) in order to extract mbfl features
  5. ``test_version_sbfl_features.py``: tests a version (set after mbfl feature extraction) in order to extract sbfl features
* list of executables for dataset analysis and reconstruction:
  * ``ranker.py``
  * ``analyzer.py``
  * ``validator.py``
  * ``reconstructor.py``

## First attempt of training and infering using a model
```
time python3 machine_learning.py --subject2setname-pair libxml2:FL-dataset-libxml2 --train --project-name model-240805-libxml2-v1 --train-validate-test-ratio 6 1 3 --epoch 10 --batch-size 1024 --stack-size 5
== Train
Total # of bug versions: 46
acc@5: 42
acc@5 perc.: 0.9130434782608695
acc@10: 44
acc@10 perc.: 0.9565217391304348

time python3 machine_learning.py --subject2setname-pair libxml2:FL-dataset-libxml2 --inference --project-name model-240805-libxml2-v1 --inference-name infer-libxml2-v1
== Infer
Total # of bug versions: 152
acc@5: 135
acc@5 perc.: 0.8881578947368421
acc@10: 144
acc@10 perc.: 0.9473684210526315

~~~~

time python3 machine_learning.py --subject2setname-pair jsoncpp:FL-dataset-jsoncpp-240803-v2 --train --project-name model-240805-jsoncpp-v1 --train-validate-test-ratio 6 1 3 --epoch 10 --batch-size 1024
==Train
Total # of bug versions: 50
acc@5: 45
acc@5 perc.: 0.9
acc@10: 48
acc@10 perc.: 0.96

time python3 machine_learning.py --subject2setname-pair jsoncpp:FL-dataset-jsoncpp-240803-v2 --inference --project-name model-240805-jsoncpp-v1 --inference-name infer-jsoncpp-v1
==Infer
Total # of bug versions: 165
acc@5: 156
acc@5 perc.: 0.9454545454545454
acc@10: 161
acc@10 perc.: 0.9757575757575757

```

last updated Aug 05, 2024
