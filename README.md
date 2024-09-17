# Fault Localization Dataset Generator for C/C++ Subjects

# 1. Dependencies
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
  * matplotlib
  * shutil
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

# 2. Build Step
## 2.1 Build MUSICUP
```
$ cd ./tools/MUSICUP/
$ make LLVM_BUILD_PATH=/usr/lib/llvm-13 -j20
```

### 2.2 Build extractor
```
$ cd ./tools/extractor/
$ make -j20
```

# 3. Executables Overview
* directory: ``src/``
* list of executables for dataset generation:
  1. ``collect_buggy_mutants.py``
  2. ``select_usable_versions.py``
  3. ``prepare_prerequisites.py``
  4. ``extract_mbfl_features.py``
  5. ``extract_sbfl_features.py``

* list of executables for dataset generation on a single version of a subject:
  1. ``test_mutant_buggy_collection.py``: tests a mutant for buggy collections (version saved when considered as buggy)
  2. ``test_version_usability_check.py``: tests a buggy mutant for usability check (version saved when considered as usable)
  3. ``test_version_prerequisites.py``: tests a version (from usable_buggy_versions) in order to extract (prepare) prerequisite data
  4. ``test_version_mbfl_features.py``: tests a version (that includes prerequisite data) in order to extract mbfl features
  5. ``test_version_sbfl_features.py``: tests a version (set after mbfl feature extraction) in order to extract sbfl features

* other executables for analysis, reconstruction, training/inferring with ML:
  * ``ranker.py``
  * ``analyzer.py``
  * ``validator.py``
  * ``reconstructor.py``
  * ``machine_learning.py``

# 5. Configurations
Users are required to give an experiment configurations written on ``./configs/config.json`` file and ``./configs/machines.json`` file and subject configurations within subject directory, ``./subjects/<subject-name>/``.

## 5.1 Experiment Configurations
### 5.1.2 ``config.json``
The following code box shows an example of written ``config.json`` file for experiment configurations.
```
{
    "use_distributed_machines": false,
    "single_machine": {
        "name": "00.000.00.00",
        "cores": 64,
        "homedirectory": "/mnt/storage2/yangheechan/"
    },
    "number_of_versions_to_check_for_usability": 10000,
    "max_mutants": 20,
    "number_of_lines_to_mutation_test": 50,
    "abs_path_to_gcovr_executable": "/usr/local/bin/gcovr",
    "gcovr_version": 7.2
}
```

### 5.1.2 ``config.json`` field explanation
  * ``use_distributed_machines``: either ``true`` or ``false`` to indicate the availability of utilization of distributed machines. If ``true``, the details of each distributed machines should be written within ``./configs/machines.json`` file (detailed explanation found in section 5.1.3).
  * ``single_machine``: 3 features of the current using machine
    * ``name``: name or address when connecting to the machine.
    * ``core``: an integer value indicating the number of available cores of the machine.
    * ``homedirectory``: absolute path to home directory
  * ``number_of_versions_to_check_for_usability``: the number of buggy mutants to check for usability (detailed explanation found in section 6.2). All buggy versions is checked if the number is greater than the number of buggy versions within ``./out/<subject-name>/<buggy-versions-directory>/``.
  * ``max_mutants``: an integer value indicating the number of maximum mutants to generate on a single line during MBFL feature extraction.
  * ``number_of_lines_to_mutation_test``: an integer value indicating the number of lines to conduct mutation testing during MBFL feature extraction.
  * ``abs_path_to_gcovr_executable``: absolute path to ``gcovr`` executable for coverage processing.
  * ``gcovr_version``: the version of ``gcovr``

### 5.1.3 ``machines.json``
The following code box shows an example of written ``machines.json`` for experiment configurations. 
```
{
    "faster4.swtv": {
        "cores": 8,
        "homedirectory": "/home/yangheechan/"
    },
    "faster5.swtv": {
        "cores": 8,
        "homedirectory": "/home/yangheechan/"
    } ...
}
```

### 5.1.4 ``machines.json`` field aplanation
This configuration file must contain a dictionary that writes key as the machine's connecting address or name and value as machine information.
  * ``cores``: number of of cores
  * ``homedirectory``: the absolute path to homedirectory.

In addition, the main server and the distributed servers must share their public key in order for enabling connecting without request of password.


## 5.2 Subject Configurations
All information (subject repository, subject configurations, etc.) must be placed within ``./subjects`` directory. Therefore, user is required to first make ``./subjects`` directory. To explain subject configuration, this section 5.2 will show an example of how subject configuration should be structured and written in standard of subject ``libxml2``.

### 5.2.1 Subject's main directory
  1. Make subject directory
      ```
      mkdir -p ./subjecst/libxml2/
      ```

  2. Copy or clone or download subject repository (source files, test files, build scripts, etc.) within subject directory, ``./subjects/libxml2`` as the same name as the directory.
      ```
      cd ./subjects/libxml2
      git clone <libxml2-link> libxml2
      ```

#### 5.2.2 Subject's real world buggy versions directory
  3. Make a directory, ``real_world_buggy_versions`` which will contain details of real world bugs found by user.
      * details of each bug is contained in a directory of its own.
      * The details must contain:
        1. ``./real_world_buggy_versions/buggy_code_file/<source-file>``: the source file version which contains the buggy code line
        2. ``./real_world_buggy_versions/testsuite_info/*``: which contains ``failing_tcs.txt`` and ``passing_tcs.txt``, in which both files writes a list of test case bash script name, ``<tc-id>.sh``.
        3. ``bug_info.csv``: a csv of 3 feature and 1 row in following order
          * ``target_code_file``: path to target code file (ex. libxml2/HTMLparser.c)
          * ``buggy_code_file``: name of ``<source-file>`` in ``./real_world_buggy_versions/buggy_code_file/`` directory
          * ``buggy_lineno``: line number of the buggy line within ``<source-file>``
      ```
      cd ./subjects/libxml2
      mkdir real_world_buggy_versions
      ```

#### 5.2.3 Subject's configurations information and script to build, clean, etc.
  4. ``./subjects/libxml2/configurations.json``: the following code box shows an example of ``configurations.json`` for a subject.
      * ``subject_name``: name of the subject
      * ``configuration_script_working_directory``: the directory in which ``configure_no_cov_script.sh`` and ``configure_yes_cov_script.sh`` must be executed.
      * ``build_script_working_directory``: the directory in which ``build_script.sh`` and ``clean_script.sh`` must be executed.
      * ``compile_command_path``: path where the ``compile_commands.json`` is generated after building the subject.
      * ``test_case_directory``: path to ``testcases/`` directory. Users MUST MAKE THIS DIRECTORY which contains bash scripts for executing individual test case, ``<tc-id>.sh``, in following formatted name, TC1.sh, TC2.sh...
      * ``subject_language``: a string value of either ``"C"`` or ``"CPP"`` indicating the programming language of the subject.
      * ``target_files``: list of files to be targetted for FL feature extraction.
      * ``target_preprocessed_files``: preprocessed files for each target files.
      * ``real_world_buggy_versions``: boolean value ``true`` or ``false`` indicating the existance of user found real world buggy versions.
      * ``environment_settings``: required environmental settings before test case execution.
      * ``cov_compiled_with_clang``: boolean value ``true`` or ``false`` indicating whether the subject for coverage was built with clang.
      * ``gcovr_source_root``: absolute path to root directory of source files (only given when ``cov_compiled_with_clang`` is ``false``, ``"None"`` if ``true``)
      * ``gcovr_object_root``: absolute path to directory where object files are saved (only given when ``cov_compiled_with_clang`` is ``false``, ``"None"`` if ``true``).
      * ``test_initialization``: command (``init_cmd``) and command working directory path (``execution_path``) if exists (``status``).
      ```
      {
          "subject_name": "libxml2",
          "configure_script_working_directory": "libxml2/",
          "build_script_working_directory": "libxml2/",
          "compile_command_path": "libxml2/compile_commands.json",
          "test_case_directory": "libxml2/testcases/",
          "subject_language": "C",
          "target_files": [
              "libxml2/parser.c",
              "libxml2/HTMLparser.c",
              "libxml2/relaxng.c",
              "libxml2/xmlregexp.c",
              "libxml2/xmlschemas.c"
          ],
          "target_preprocessed_files": [
              "libxml2/parser.i",
              "libxml2/HTMLparser.i",
              "libxml2/relaxng.i",
              "libxml2/xmlregexp.i",
              "libxml2/xmlschemas.i"
          ],
          "real_world_buggy_versions": true,
          "environment_setting": {
              "needed": true,
              "variables": {
                  "LD_LIBRARY_PATH": "libxml2/.libs"
              }
          },
          "cov_compiled_with_clang": true,
          "gcovr_source_root": "None",
          "gcovr_object_root": "None",
          "test_initialization": {
              "status": false,
              "init_cmd": "None",
              "execution_path": "None"
          }
      }
      ```
  5. Build script for subject written in ``build_script.sh``. Must return 1 at build failure, 0 else.
  6. Clean script for subject written in ``clean_script.sh``.
  7. Configuration script for building subject with coverage ``confure_yes_cov_script.sh``.
  8. Configuration script for building subject without coverage ``confure_yes_cov_script.sh``.


# 6. Detailed Steps and Execution for Fault-Localization Dataset Generation
## 6.1 Buggy Mutant Collection
### 6.1.1 Action for Step 6.1
  1. **generates** mutants on lines of target source files indicated in the parameter ``target_files`` of ``./subjects/libxml2/configurations.json`` utilizing ``musicup``, a mutation generation tool for C/C++ (mutant source files saved within ``./out/<subject-name>/generated_mutants`` directory).
  2. **executes** test cases (test case bash scripts) positioned within the directory indicated in the parameter ``test_case_directory`` of ``./subjects/libxml2/configurations.json``. 
  3. **saves** mutants that cause a test case to fail within ``./out/<subject-name>/buggy_mutants/`` directory with indication of failing, passing, crashing test cases.

### 6.1.2 CLI for buggy mutant collection
```
$ time python3 collect_buggy_mutants.py --subject <subject-name> [--verbose]
```
* command flag usage:
  * ``--subject <str>``: name of the target subject

## 6.2 Usable Buggy Mutant Collection
### 6.2.1 Action for Step 6.2
  1. **selects** ``N`` amount of mutants within ``./out/<subject-name>/buggy_mutants/`` in which ``N`` is the number given in the paramter ``number_of_versions_to_check_for_usability`` of ``./configs/config.json``. (A limit ``N`` is given because there can be quite many buggy mutants to check with limitted amount of time).
  2. **executes** failing TCs and measures coverage
  3. **saves** mutants (to ``./out/<subject-name>/usable_buggy_mutants/`` directory) that...
      * buggy line is covered by failing TCs line
      * have at least 1 failing TC and 1 passing TC

### 6.2.2 CLI for Usable Buggy Mutant Collection
```
$ time python3 select_usable_versions.py --subject <subject-name>
```
* command flag usage:
  * ``--subject  <str>``: name of the target subject

### 6.2.3 Validation command for Usable Buggy Mutants
For each buggy versions within ``usable_buggy_versions`` directory, the following ``validator.py`` command validates that:
  * ``bug_info.csv`` has been generated
  * ``testsuite_info`` has been generated for both failing and passing test cases
  * ``buggy_code_file`` directory contains the designated buggy code file
```
$ python3 validator.py --subject <subject-name> --set-name <usable_buggy_versions-directory> --validate-usable-buggy-versions
```

## 6.3 Prerequisite Data Preparation
### 6.3.1 Action for Step 6.3
  1. Prepares the following prerequisite data for mutants (and real world buggy versions) included in ``./out/<subject-name>/usable_buggy_mutants/`` directory by executing all test cases:
      * postprocessed coverage information (CSV format)
      * line-to-function map information (JSON format)
      * lines executed by failing TCs (JSON format)
      * lines executed by passing TCs (JSON format)
      * coincidentally-correct-test-cases (CCTs optional)

### 6.3.2 CLI for prerequisite data preparation
```
$ time python3 prepare_prerequisites.py --subject <subject-name> --target-set-name <usable_buggy_versions-directory> [--use-excluded-failing-tcs] [--passing-tcs-perc 0.05] [--failing-tcs-perc 0.1]
```
* command flag usage:
  * ``--subject <str>``: name of the target subject
  * ``--target-set-name <str>``: name of the directory that contains buggy versions targeted for prerequisite data preparation

### 6.3.3 Validation command for Prerequisite Data
For each buggy versions within ``prerequisite_data`` directory, the following ``validator.py`` command validates that:
  * ``buggy_line_key.txt`` has been generated
  * ``coverage_summary.csv`` has been generated
  * ``postprocess_coverage.csv`` has been generated
  * failing TCs executes the buggy line based on ``postprocessed_coverage.csv`` file
  * ``lines_executed_by_failing_tc.json`` has been generated
  * ``line2function.json`` has been generated
  * at least 1 failing tc and 1 passing tc exists
```
$ python3 validator.py --subject <subject-name> --set-name <prerequisite_data-directory> --validate-prerequisite-data
```

### 6.3.4 Statistics result generation command for Prerequisite Data
The following commands generates statistics regarding the prerequisite data and crashed buggy mutants information within ``./statistics/<subject-name>/`` directory.
```
$ python3 analyzer.py --subject <subject-name> --set-name <prerequisite_data-directory> --output-csv <prerequisite_data-directory>-tc-stats --prerequisite-data --removed-initialization-coverage
$ python3 analyzer.py --subject <subject-name> --set-name crashed_buggy_mutants --output crashed_buggy_mutants --crashed-buggy-mutants
```

## 6.4 MBFL Feature Extraction
### 6.4.1 Action for step 6.4
  1. **generates** at maximum ``N`` amount of mutants on randomly selected ``X`` (at max) number of lines executed by failing TCs, where ``N`` is the number given in the parameter ``max_mutants`` and ``X`` is the number given in the parameter ``number_of_lines_to_mutation_test`` of ``./configs/config.json``, for mutants saved within ``./out/<subject-name>/<prerequisite_data-directory>/`` directory.
  2. conducts MBFL on with the generated mutants
  3. **saves** the results to ``./out/<subject-name>/mbfl_features/`` directory

### 6.4.2 CLI for mbfl feature extraction
```
$ time python3 extract_mbfl_features.py --subject <subject-name> --target-set-name <prerequisite_data-directory> --trial <trial-name> [--exclude-init-lines] [--parallel-cnt 2] [--dont-terminate-leftovers] [--remain-one-bug-per-line]
```
* command flag usage:
  * ``--subject <str>``: name of the target subject
  * ``--target-set-name <str>``: name of the directory that contains buggy versions targeted for mbfl feature extraction
  * ``--trial <str>``: name of the experiment trial (ex. trial1)
  * ``--exclude-init-lines``: flag when given, excludes lines executed during initialization (before test case execution) from MBFL targeted lines
  * ``--prallel-cnt <int>``: conduct MBFL feature extraction of a buggy version in parallel of ``<int>`` amount.
  * ``--dont-terminate-leftovers``: flag when given, waits until all mbfl exctraction of buggy versions has been finished in a batch.
  * ``--remain-one-bug-per-line``: flag when given, only selects one buggy version per line.

### 6.4.3 Validation command for MBFL features
For each buggy versions within ``mbfl_features`` directory, the following ``validator.py`` command validates that:
  * ``mbfl_features.csv`` has been generated
  * ``mbfl_features.csv`` only contains one buggy line
  * ``selected_mutants.csv`` has been generated
  * ``mutation_testing_results.csv`` has been generated
```
$ python3 validator.py --subject <subject-name> --set-name <mbfl_features-directory> --validate-mbfl-features --trial <trial-name>
```

### 6.4.4 Statistics results generation command for MBFL features
The following commands generates statistics regarding the rank and statistical information of mbfl features data within ``./statistics/<subject-name>/`` directory.
```
$ python3 ranker.py --subject <subject-name> --set-name <mbfl_features-directory> --output-csv <mbfl_features-directory>-rank-stats --mbfl-features --trial <trial-name>
$ python3 analyzer.py --subject <subject-name> --set-name <mbfl_features-directory> --output-csv <mbfl_features-directory>-tc-stats --prerequisite-data --removed-initialization-coverage
```

## 6.5 SBFL Feature Extraction
### 6.5.1 Action for step 6.5
  1. extract SBFL feature based on the postprocessed coverage information measured on step 6.3.
  2. **saves** the results to ``./out/<subject-name>/sbfl_features/`` directory

### 6.5.2 CLI for mbfl feature extraction
```
$ time python3 extract_sbfl_features.py --subject <subject-name> --target-set-name <mbfl_features-directory>
```
* command flag usage:
  * ``--subject <str>``: name of the target subject
  * ``--target-set-name <str>``: name of the directory that contains buggy versions targeted for sbfl feature extraction

### 6.5.3 Validation command for SBFL features
For each buggy versions within ``sbfl_features`` directory, the following ``validator.py`` command validates that:
  * ``sbfl_features.csv`` has been generated
```
$ python3 validator.py --subject <subject-name> --set-name <sbfl_features-directory> --validate-sbfl-features
```

### 6.5.4 Statistics results generation command for SBFL features
The following commands generates statistics regarding the rank information of sbfl features data within ``./statistics/<subject-name>/`` directory.
```
$ python3 ranker.py --subject <subject-name> --set-name <sbfl_features-directory> --output-csv <sbfl_features-directory>-rank-stats --sbfl-features
```

## 6.6 FL Feature Dataset Finalization (combing MBFL and SBFL features)
### 6.6.1 Action for step 6.6
  1. combine both sbfl and mfbl feature to a single csv file.
### 6.6.2 CLI for FL feature dataset finalization
```
$ python3 reconstructor.py --subject <subject-name> --set-name <sbfl_features-directory> --combine-mbfl-sbfl --combining-trials trial1
```
* command flag usage:
  * ``--subject <str>``: name of the target subject
  * ``--target-set-name <str>``: name of the directory that contains buggy versions targeted for mbfl and sbfl combining action
  * ``--combine-mbfl-sbfl``: flag when given, combines mbfl and sbfl feature csv file within buggy versions of targetted directory
  * ``--combining-trials [<str> ...]``: name of the trials to combine

### 6.6.3 Validation command for FL features
For each buggy versions within ``FL-dataset-<subject-name>`` directory, the following ``validator.py`` command validates that:
  * there is only one row with "bug" column as 1 within the ``<bug-id>.fl_features.csv``
  * the the sum of SBFL spectrum (ep, ef, np, nf) add up to the utilized number of test cases
  * all failing tcs executes buggy line based on postprocess coverage csv file
  * Metallaxis and MUSE score is correctly measurable with the given features
  * the mutated code exists within the specified line of buggy code file
```
$ python3 validator.py --subject <subject-name> --set-name FL-dataset-<subject-name> --validate-fl-features
```

# 7. Steps to training ML and inferring

## 7.1 Postprocessing FL feature data
```
$ python3 machine_learning.py --subject2setname-pair <subject-name>:<fl-dataset-directory> --postprocess-fl-features
```

## 7.2 train/validae/test MLP model
```
$ python3 machine_learning.py --subject2setname-pair <subject-name>:<fl-dataset-directory> --train --project-name ML-<date>-<subject-name>-<version> --train-validate-test-ratio 6 1 3 --random-seed 42 --epoch 20 --batch-size 1024 --learning-rate 0.001 --dropout 0.2 --model-shape 35 64 32 1
```

## 7.3 inferring with MLP model
```
$ python3 machine_learning.py --subject2setname-pair <subject-name>:<fl-dataset-directory> --inference --project-name ML-<date>-<subject-name>-<version> --inference-name infer-<subject-name>-<version>
```


---
last updated Aug 22, 2024
