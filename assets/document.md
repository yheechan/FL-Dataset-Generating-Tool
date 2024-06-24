# 결함 위치 탐지 데이터셋 구축 방법 정리
결함 위치 탐지 데이터셋은 하나의 소프트웨어 서브젝트에 대하여 테스트 케이스를 실행하여 동적 특징을 추출한다. 동적 특징으로는 스펙트럼 기반 (SBFL: Spectrum-Based Fault Localization)과 변이 기반 (MBFL: Mutation-Based Fault Localization) 특징 데이터를 포함하고 있다.

## 1. 사용자로 부터 요구되는 정보
결함 위치 탐지 데이터셋 구축 도구를 사용하기 위해 사용자로부터 요구되는 정보는 다음과 같다:
  * ``build_script.sh``: 서브젝트의 build 명령어
  * ``clean_script.sh``: 서브젝트의 build 내용 clean 명령어
  * ``configuration.json``: 1.2 섹션에서 설명

### 1.2 ``configuration.json`` 요구되는 정보
* ``subject_name``: 서브젝트 이름
* ``configure_script_working_directory``: configure 명령 스크립트가 실행 되는 디렉토리 위치
* ``build_script_working_directory``: build와 clean 명령 스크립트가 실행 되는 디렉토리 위치
* ``compile_command_path``: compile command, ``compile_commands.json`` 파일의 위치
* ``test_case_directory``: 테스트 케이스 스크립트들이 모여있는 디렉토리 위치
* ``subject_language``: 서브젝트의 프로그래밍 언어 (``C`` 혹은 ``CPP``)

### 1.1 libxml2 서브젝트의 예시
```
subjects/
└── libxml2
    ├── build_script.sh
    ├── clean_script.sh
    ├── configurations.json
    ├── configure_no_cov_script.sh
    ├── configure_yes_cov_script.sh
    ├── libxml2
    └── real_world_buggy_versions

configs/
├── config.json
└── machines.json
```



## 2. 단계
1. 테스트 케이스 준비 (수동 작업)
2. 실제 버그 버전 수집 (수동 작업)
3. 인공 버그 버전 수집
4. FL 데이터셋 구축에 필요한 데이터 수집
  * 각 테스트 케이스 별 커버리지 정보
  * 각 라인이 해당되는 함수 매핑 정보
  * 실패하는 테스트 케이스가 실행하는 라인 정보
5. MBFL 특징 추출
6. SBFL 특징 추출
7. 최종 FL 데이터셋 완성



### 2.1. 테스트 케이스 준비
테스트 케이스 준비 단계에서는 대상 서브젝트에 대하여 고유하게 실행 할 수 있는 테스트 케이스를 준비해야한다.
  * 하나의 테스트 케이스는 고유한 테스트 케이스 ID 준비 (예: TC1, TC2, ... TC100)
  * 고유한 테스트 케이스 ID로부터 해당 테스트 케이스를 실행 할 수 있게 코드 수정
  * 테스트 케이스의 통과 및 실패 판별 할 수 있는 오라클 준비

### 2.2. 실제 버그 버전 수집
실제 버그 버전 수집 단계에서는 오픈 소스 서브젝트 경우에 수집이 가능하며, 깃허브와 같은 서브젝트 리포지토리에 공유가 된 버그들을 수동으로 수집한다. 이때 다음 정보들을 수작업으로 준비해야한다:
  * ``buggy_code_file/<buggy-code-file>``: 버그를 유발하는 버전의 소스 코드 파일
  * ``testsuite_info/``: 해당 디렉토리에 ``passing_tcs.txt``와 ``failing_tcs.txt``파일. 각 파일은 해당 버그 버전 서브젝트에 적용하여 테스트 케이스들을 실행 했을 때 통과하는 테스트 케이스와 실패하는 테스트 케이스 정보를 담는다.
  * ``bug_info.csv``: 해당 파일에는 다음 정보들이 포함되어야 한다.
    * ``<target-code-file>``: 대상 서브젝트에 버기 코드가 적용 되어야하는 소스 코드 파일 명칭
    * ``<buggy-code-file>``: ``buggy_code_file/`` 디렉토리에 저장된 버기 코드 파일 명칭
    * ``<buggy-lineno>``: 버그가 위치하고 있는 버기 라인 번호

### 2.3. 인공 버그 버전 수집
인공 버그 버전 수집 단계에서는 대상 소브젝트로부터 인공 버그를 투입하여 인공 버그를 수집한다.
  1. 대상 소브젝트의 지정된 소스 코드 파일에 많은 변이 생성
  2. 생성 된 변이를 소스 코드에 적용하여 각 테스트 케이스들을 실행
  3. 실패하는 테스트 케이스가 있는 인공 버그 버전 저장

#### 2.3.1 명령어 실행 방법
```
usage: collect_buggy_mutants.py [-h] --subject SUBJECT [--verbose]

Copy subject to working directory

optional arguments:
  -h, --help         show this help message and exit
  --subject SUBJECT  Subject name
  --verbose          Verbose mode
```


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
