# Fault Localization Dataset Generator for C/C++ Subjects

## Dependencies
* LLVM 13.0.1
  * link: https://apt.llvm.org/
  * required to install "all" packages of LLVM ($ sudo ./llvm.sh 13 all)

* python 3.8
* gcovr 6.0
* bear 2.3.11
* GNU make 4.1
* cmake 3.10.2

* rsync  version 3.1.2  protocol version 31
* diff (GNU diffutils) 3.6
* GNU patch 2.7.6

* VIM - Vi IMproved 8.0
* OpenSSH_7.6p1 Ubuntu-4ubuntu0.7, OpenSSL 1.0.2n

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

last updated June 21, 2024
