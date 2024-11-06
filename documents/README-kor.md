# Fault Localization Dataset Generator for C/C++ Subjects
이 프로젝트는 결함위치탐 (FL: Fault Localization) 데이터셋 생성하는 도구로 만들어졌다. 하나의 프로젝트에 대하여 결함위치탐지 데이터셋은 다음과 같은 단계를 거쳐 생성 된다:
1. 변이기반 버그 버전 생성
2. 버그 버전 사용 가능 여부 검증
3. 결함위치탐지 데이터셋에 필요한 사전 데이터 추출
4. 변이기반 (MBFL: Mutation-Based) 데이터셋 추출
5. 스펙트럼기반 (SBFL: Spectrum-Based) 데이터셋 추출

이 보고서는 해당 도구에 대한 사용법을 알려준다.

# 1. 의존 도구
* LLVM 13.0.1
  * link: https://apt.llvm.org/
  * required to install "all" packages of LLVM ($ sudo ./llvm.sh 13 all)
* python 3.8
* gcovr 6.0 (and above)
* bear 2.3.11
* GNU make 4.1
* cmake 3.10.2
* rsync  version 3.1.2  protocol version 31
* diff (GNU diffutils) 3.6
* GNU patch 2.7.6

# 2. 도구 빌드 과정
## 2.1 MUSICUP 빌드
* ``MUSICUP``은 C/C++ 소스 코드 파일에 대하여 변이를 생성해주는 용도로 사용된다.
* 빌드 명령어는 다음과 같다:
```
$ cd ./tools/MUSICUP/
$ make LLVM_BUILD_PATH=/usr/lib/llvm-13 -j20
```

### 2.2 extractor 빌드
* ``extract``은 C/C++ 소스 코드에 대하여 라인-함수 매핑 정보를 추출해주는 용도로 사용된다
```
$ cd ./tools/extractor/
$ make -j20
```

# 3. 실행 파일 개요
결함위치탐지 데이터셋 생성 도구는 총 6개 실행 파일로 나누어 작동한다. 모든 실행 파일은 ``./src/`` 폴더에 있으며 해당 위치에서 실행 할 수 있다.

* 결함위치탐지 데이터셋 생성을 위한 실행 파일 목록:
  1. ``collect_buggy_mutants.py``: 프로젝트에 대하여 변이를 심어 버그 버전을 생성한다.
  2. ``select_usable_versions.py``: 생성된 버그 버전에서 사용 가능한 버그 버전을 추려 검증한다.
  3. ``prepare_prerequisites.py``: 결함위치탐지 데이터셋에 필요한 사전 데이터들을 추출한다.
  4. ``extract_mbfl_features.py``: 사전 추출된 데이터로부터 변이기반 데이터셋을 추출한다.
  5. ``extract_sbfl_features.py``: 사전 추출된 데이터로부터 스펙트럼기반 데이터셋을 추출한다.
  6 ``reconstructor.py``: 변이기반과 스펙트럼기반 데이터셋을 합치는 작업을 수행한다.


* 결함위치탐지 데이터셋 검증과 분석을 위한 실행 파일 목록:
  * ``ranker.py``: 결함위치탐지 데이터셋에 대하여 변이기반과 스펙트럼기반 정확도 계산한다.
  * ``analyzer.py``: 결함위치탐지 데이터셋에 대하여 통계자료 (e.g., 테스트 케이스의 개수, 커버리지 정보, 등)계산한다.
  * ``validator.py``: 결함위치탐지 데이터셋의 유효함을 검증한다.
  * ``machine_learning.py``: 최종 결함위치탐지 데이터셋으로 다층 퍼셉트론 (MLP: Multi-Layered Perceptron) 모델 학습과 시험을 수행한다.


# 4. 결함위치탐지 데이터셋 도구 사용법

# 5. Configuration 설정
결함위치탐지 데이터셋 생성 작업을 수행하기 앞서 데이터셋 추출에 대한 구성요소를 ``./configs/config.json``, ``./configs/machines.json`` 파일에 그리고 대상 프로젝트에 대한 구성요소를 ``./subject/<subject-name>/`` 디렉토리에 설정해야 한다. 설정 방법은 5.1장과 5.2장에 설명한다.

## 5.1 실험 (FL 데이터셋 생성)에 대한 Configuration 설정 방법
### 5.1.2 ``./configs/config.json`` 파일 설정
``./configs/config.json`` 파일은 실험에 대한 configuration을 다음과 같은 형식으로 설정한다.
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

### 5.1.3 ``./configs/config.json``의 설정 값 (변수) 설명
  * ``use_distributed_machines``: 분산 시스템 활용이 가능할 시``true``, 그렇지 않을 시 ``false``로 설정한다. ``true``로 설정할 ``./configs/machines.json`` 파일에 분산 시스템 정보를 입력해야 한다. 이에 대한 자세한 설명은 5.1.4장에서 볼 수 있다.
  * ``single_machine``: 현재 사용중인 서버의 정보를 설정해준다.
    * ``name``: 서버의 이름 혹은 ip 주소.
    * ``core``: 현재 사용중인 서버의 core 개수.
    * ``homedirectory``: 현재 사용중인 서버의 홈 디렉토리.
  * ``number_of_versions_to_check_for_usability``: 사용 가능성에 대한 검증을 거칠 버그 버전에 개수. 해당 변수는 결함위치탐지 데이터셋 생성의 2단계에서 사용되며 자세한 설명은 6.2장에서 볼 수 있다.
  * ``max_mutants``: 변이기반 데이터셋 생성 시 각 라인별 생성 할 변이의 최대 개수.
  * ``number_of_lines_to_mutation_test``: 변이기반 데이터셋 생성 시 변이 테스트를 수행 할 코드 라인의 최대 개수.
  * ``abs_path_to_gcovr_executable``: ``gcovr`` 실행 파일의 절대 주소. 이는 프로젝트의 커버리지 정보를 추출할 때 사용된다.
  * ``gcovr_version``: ``gcovr``의 버전.


### 5.1.4 ``./configs/machines.json`` 파일 설정
``./configs/machines.json``파일은 분산 시스템 사용 가능할 시 (``use_distrbuted_machines = true``), 사용하게 될 각 분산 시스템 (서버)에 대한 정보 설정 파일이다.
```
{
    "faster4.swtv": {
        "cores": 8,
        "homedirectory": "/home/yangheechan/"
    },
    "faster5.swtv": {
        "cores": 8,
        "homedirectory": "/home/yangheechan/"
    },
    ...
}
```

### 5.1.5 ``machines.json`` field aplanation
각 분산 시스템 (서버)의 정보를 위와 같은 형식으로, 서버 접속에 사용 할 명칭 혹은 ip 주소와 서버의 core 개수와 홈디렉토리로 구성된다.
  * ``cores``: 서버의 core 개수.
  * ``homedirectory``: 서버의 홈디렉토리.

추가적으로 현재 사용중인 서버 (main server)로부터 각 분산 시스템 (서버)에 자동 접속을 위해 공개키 (public key) 공유가 되어있어야 한다.


## 5.2 프로젝트에 대한 Configurations 설정 방법 (예시 기준: libxml2 프로젝트)
프로젝트에 해당되는 모든 정보 (프로젝트 리포지토리, 프로젝트 configurations, etc.)는 ``./subjects/`` 디렉토리에 위치 시킨다. 그러므로 사용자는 가장 먼저 ``./subjects/`` 디렉토리를 생성해야 한다. 프로젝트데 대한 configuration 설정하는 방법은 5.2.1장 부터 자세한 설명을 볼 수 있다 (설명은 ``libxml2`` 프로젝트 기준으로 예를 보인다).

### 5.2.1 프로젝트의 main 디렉토리 설정
  1. ``./subject/`` 디렉토리와 프로젝트 디렉토리 생성
      ```
      mkdir -p ./subjects/libxml2/
      ```

  2. 프로젝트의 리포지토리를 ``./subjects/libxml2/`` 위치에 복사, clone, 혹은 다운으로 내려받는다 (프로젝트 리포지토리 디렉토리의 명칭은 프로젝트 명칭과 동일하게 내려받는다).
      ```
      cd ./subjects/libxml2
      git clone <libxml2-link> libxml2
      ```

#### 5.2.2 프로젝트의 실제 버그 버전 설정 방법
  3. ``./subjects/libxml2/`` 위치에 ``real_world_buggy_versions`` 이름의 디렉토리를 생성한다. 이 디렉토리는 실제 버그 버전들에 대한 정보를 담는다.
      ```
      cd ./subjects/libxml2
      mkdir real_world_buggy_versions
      cd real_world_buggy_versions
      mkdir HTMLparser.issue318.c
      ```
      * 각 실제 버그 버전들의 세부 정보는 해당의 디렉토리를 만들어 아래의 정보들을 담는다:.
        * ``./real_world_buggy_versions/<버그-버전>/buggy_code_file/<source-file>``: 버그 라인을 포함하고 있는 소스 코드 파일.
        * ``./real_world_buggy_versions/<버그-버전>/testsuite_info/*``: 해당 디렉토리에는 다음과 같은 파일을 포함 시킨다:
          * ``failing_tcs.txt``: 해당 버그 버전에서 실패하는 테스트 케이스들의 목록. 
          * ``passing_tcs.txt``: 해당 버그 버전에서 패스하는 테스트 케이스들의 목록.
          * 테스트 케이스의 목록은 각 파일의 배시 스크립트의 명칭(``<tc-id>.sh``)으로 나열한다. 각 배시 스크립트는 하나의 테스트 케이스를 실행하는 명령어가 포함되는 실행 파일이다.
        * ``./real_world_buggy_versions/<버그-버전>/bug_info.csv``: 해당 csv 파일에는 해당 버그 버전에 대하여 3개의 feature 정보를 다음과 같은 순서로 담는다:
          ```
          target_code_file,buggy_code_file,buggy_lineno
          libxml2/HTMLparser.c,HTMLparser.issue318.c,3034
          ```
          * ``target_code_file``: 프로젝트의 리포지토리 디렉토리부터 시작한 타깃 소스코드 파일 경로 (ex. ``libxml2/HTMLparser.c``)
          * ``buggy_code_file``: ``./real_world_buggy_versions/buggy_code_file/``에 저장한 ``<source-file>``의 이름.
          * ``buggy_lineno``: ``<source-file>``에 버기 라인이 위차하고 있는 라인 번호.

#### 5.2.3 프로젝트의 configurations 설정과 빌드, 정리 명령 실행 파일
  4. ``./configs/libxml2/configurations.json`` 파일은 프로젝트에 대한 configuration을 다음과 같은 형식으로 설정.
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
          "gcovr_object_root": "None"
      }
      ```
      * ``subject_name``: 프로젝트의 이름.
      * ``configuration_script_working_directory``: 프로젝트 configure 스크립트 (``configure_no_cov_script.sh`` and ``configure_yes_cov_script.sh``)가 실행 되어야 하는 경로.
      * ``build_script_working_directory``: 프로젝트의 빌드 스크립트 (``build_script.sh``)가 실행 되어야 하는 경로.
      * ``compile_command_path``: 프로젝트 빌드 후 생성 되는 ``compile_commands.json`` 파일의 경로.
      * ``test_case_directory``: 프로젝트 리포지토리에 테스트 케이스 실행 스크립트들이 저장된 디렉토리 (``testcases/``)의 경로. 사용자는 필수적으로 ``testcases/`` 명칭으로 디렉토리를 만든 후, 각 테스트 케이스를 실행하는 배시 스크립트(``<tc-id>.sh``)를 ``TC1.sh``, ``TC2.sh`` ... ``TC<N>.sh`` 형식으로 만들오 해당 디렉토리의 위치 시켜야 한다.
      * ``subject_language``: 해당 프로젝트의 프로그래밍 언어를 ``"C"`` 혹은 ``"CPP"``로 입력한다.
      * ``target_files``: 결함위치탐지 데이터셋 생성에 타깃으로 하는 소스코드 파일의 목록.
      * ``target_preprocessed_files``: 결함위치탐지 데이터셋 생성에 타깃으로 하는 소스코드 파일들의 전처리 파일의 목록.
      * ``real_world_buggy_versions``: 실제 버그 버전이 있을 시 ``true``, 실제 버그 버전이 없을 시 ``false``로 설정한다.
      * ``environment_settings``: 프로젝트 테스트 케이스를 실행 하기 위해 요구되는 환경 변수 설정 값.
        * ``needed``: 환경 변수 설정 필요 시 ``true`` 그렇지 않을 시 ``false``.
        * ``variables``: 테스트 케이스 실행에 필요한 환경 변수 설정 값의 목록.
      * ``cov_compiled_with_clang``: 프로젝트 빌드 명령이 ``clang`` 컴파일러를 사용 할 시 ``true``, ``gcc`` 컴파일러를 사용 할 시 ``false``.
      * ``gcovr_source_root``: 소스 코드 파일의 절대 경로. 이는 ``cov_compiled_with_clang`` 변수가 ``false``일 때 절대 경로로 설정해주며, ``cov_compiled_with_clang``이 ``true``일 때는 ``"None"``으로 설정해준다.
      * ``gcovr_object_root``: 소스 코드 파일의 object 파일이 저장 되는 절대 경로. 이는 ``cov_compiled_with_clang`` 변수가 ``false``일 때 절대 경로로 설정해주며, ``cov_compiled_with_clang``이 ``true``일 때는 ``"None"``으로 설정해준다.
  5. ``./configs/libxml2/build_script.sh`` 이름으로 프로젝트 빌드 명령어로 실행 파일을 만든다. 이때 빌드가 실패할 때 1 값을, 성공할 시 0 값을 돌려주게 만든다.
      ```
      bear make -j20 runtest
      ```
  6. ``./configs/libxml2/clean_script.sh`` 이름으로 프로젝트 빌드 정리 명령어로 실행 파일을 만든다.
      ```
      make clean
      ```
  7. ``./configs/libxml2/configure_yes_cov_script.sh`` 이름으로 coverage 설정을 킨 configure 명령어로 실행 파일을 만든다.
      ```
      ./make_tc_scripts.py
      ./autogen.sh CFLAGS='-O0 -fprofile-arcs -ftest-coverage --save-temps' \
                    CC='clang-13' \
                    CXX_FLAGS='-O0 -fprofile-arcs -ftest-coverage -g --save-temps' \
                    CXX='clang++' --with-threads=no
      ```
  8. ``./configs/libxml2/configure_no_cov_script.sh`` 이름으로 coverage 설정을 끈 configure 명령어로 실행 파일을 만든다.
      ```
      ./make_tc_scripts.py
      ./autogen.sh CC='clang-13' CFLAGS='-O3' \
                  CXX='clang++' CXX_FLAGS='-O0' \
                  --with-threads=no
      ```


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
      * lines executed by CCTs (Json format)
      * coincidentally-correct-test-cases

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
$ python3 ranker.py --subject <subject-name> --set-name <mbfl_features-directory> --output-csv <mbfl_features-directory>-rank-stats --mbfl-features --trial <trial-name> [--no-ccts]
$ python3 analyzer.py --subject <subject-name> --set-name <mbfl_features-directory> --output-csv <mbfl_features-directory>-tc-stats --prerequisite-data --removed-initialization-coverage
```
* command flag usage:
  * ``--no-ccts``: flag when given, measures rank of mbfl features measured without the usage of CCTs

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
$ python3 ranker.py --subject <subject-name> --set-name <sbfl_features-directory> --output-csv <sbfl_features-directory>-rank-stats --sbfl-features [--no-ccts]
```
* command flag usage:
  * ``--no-ccts``: flag when given, measures rank of sbfl features measured without the usage of CCTs

## 6.6 FL Feature Dataset Finalization (combing MBFL and SBFL features)
### 6.6.1 Action for step 6.6
  1. combine both sbfl and mfbl feature to a single csv file.
### 6.6.2 CLI for FL feature dataset finalization
```
$ python3 reconstructor.py --subject <subject-name> --set-name <sbfl_features-directory> --combine-mbfl-sbfl --combining-trials trial1 [--no-ccts] [--done-remotely]
```
* command flag usage:
  * ``--subject <str>``: name of the target subject
  * ``--target-set-name <str>``: name of the directory that contains buggy versions targeted for mbfl and sbfl combining action
  * ``--combine-mbfl-sbfl``: flag when given, combines mbfl and sbfl feature csv file within buggy versions of targetted directory
  * ``--combining-trials [<str> ...]``: name of the trials to combine
  * ``--no-ccts``: flag when given, measures rank of sbfl features measured without the usage of CCTs
  * ``--done-remotely``: flag when give, doesn't account in including generate mutatants for mbfl extraction because the data are in remote machines.

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

## 7.4 part real-world bugs from mutated bugs
```
$ python3 machine_learning.py --subject2setname-pair <subject-name>:<fl-dataset-directory> --part-real-world-bugs --real-world-bugs [<str> ...]
```

---
last updated Sep 26, 2024
