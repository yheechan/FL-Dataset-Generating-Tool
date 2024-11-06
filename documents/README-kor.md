# 결함위치탐지 데이터셋 새성 도구 (C/C++ 서브젝트 대상)
이 프로젝트는 결함위치탐 (FL: Fault Localization) 데이터셋 생성하는 도구로 만들어졌다. 하나의 프로젝트에 대하여 결함위치탐지 데이터셋은 다음과 같은 단계를 거쳐 생성 된다:
1. 변이기반 버그 버전 생성
2. 버그 버전 사용 가능 여부 검증
3. 결함위치탐지 데이터셋 생성에 필요한 사전 데이터 추출
4. 변이기반 (MBFL: Mutation-Based) 데이터셋 추출
5. 스펙트럼기반 (SBFL: Spectrum-Based) 데이터셋 추출
6. 변이기반과 스펙트럼기반 데이터 병합하여 최종 결함위치탐지 데이터셋 생성

이 보고서는 해당 도구에 대한 사용법을 알려준다.

# 0. 목차
* [0. 목차](#0-목차)
* [1. 의존 도구](#1-의존-도구)
* [2. 도구 빌드 과정](#2-도구-빌드-과정)
  * [2.1 ``MUSICUP`` 빌드](#21-musicup-빌드)
  * [2.2 ``extractor`` 빌드](#22-extractor-빌드)
* [3. 실행 파일 개요](#3-실행-파일-개요)
* [4. configuration 설정 방법](#4-configuration-설정-방법)
* [5. 결함위치탐지 데이터셋 생성 단계별 실행 방법](#5-결함위치탐지-데이터셋-생성-단계별-실행-방법)
  * [5.1 [1단계] 변이기반 버그 버전 생성](#51-1단계-변이기반-버그-버전-생성)
  * [5.2 [2단계] 버그 버전 사용 가능 여부 검증](#52-2단계-버그-버전-사용-가능-여부-검증)
  * [5.3 [3단계] 결함위치탐지 데이터셋 생성에 필요한 사전 데이터 추출](#53-3단계-결함위치탐지-데이터셋-생성에-필요한-사전-데이터-추출)
  * [5.4 [4단계] 변이기반 데이터셋 추출](#54-4단계-변이기반-mbfl-mutation-based-데이터셋-추출)
  * [5.5 [5단계] 스펙트럼기반 데이터셋 추출](#55-5단계-스펙트럼기반-sbfl-spectrum-based-데이터셋-추출)
  * [5.6 [6단계] 최종 결함위치탐지 데이터셋 생성](#56-6단계-변이기반과-스펙트럼기반-데이터-병합하여-최종-결함위치탐지-데이터셋-생성)


# 1. 의존 도구
* LLVM 13.0.1
  * 버전: 13.0.1 (이 외 버전 사용 불가)
  * 설치 방법 링크: https://apt.llvm.org/
  * 설치 명령어:
    ```
    $ wget https:/apt.llvm.org/llvm.sh
    $ chmod +x llvm.sh
    $ sudo ./llvm.sh 13 all
    ```
* python
  * 버전: 3.8
* Python Modules
  * 실행 명령어:
    ```
    $ pip install -r requirements.txt
    ```
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
* ``extractractor``은 C/C++ 소스 코드에 대하여 라인-함수 매핑 정보를 추출해주는 용도로 사용된다
  ```
  $ cd ./tools/extractor/
  $ make -j20
  ```

# 3. 실행 파일 개요
결함위치탐지 데이터셋 생성 도구는 총 6개 실행 파일로 나누어 작동한다. 모든 실행 파일은 ``./src/`` 폴더에 있으며 해당 위치에서 실행 할 수 있다.

* 결함위치탐지 데이터셋 생성을 위한 실행 파일 목록:
  1. ``collect_buggy_mutants.py``: 서브젝트에 대하여 변이를 심어 버그 버전을 생성한다.
  2. ``select_usable_versions.py``: 생성된 버그 버전에서 사용 가능한 버그 버전을 추려 검증한다.
  3. ``prepare_prerequisites.py``: 결함위치탐지 데이터셋에 필요한 사전 데이터들을 추출한다.
  4. ``extract_mbfl_features.py``: 사전 추출된 데이터로부터 변이기반 데이터셋을 추출한다.
  5. ``extract_sbfl_features.py``: 사전 추출된 데이터로부터 스펙트럼기반 데이터셋을 추출한다.
  6. ``reconstructor.py``: 변이기반과 스펙트럼기반 데이터셋을 합치는 작업을 수행한다.


* 결함위치탐지 데이터셋 검증과 분석을 위한 실행 파일 목록:
  * ``ranker.py``: 결함위치탐지 데이터셋에 대하여 변이기반과 스펙트럼기반 정확도 계산한다.
  * ``analyzer.py``: 결함위치탐지 데이터셋에 대하여 통계자료 (e.g., 테스트 케이스의 개수, 커버리지 정보, 등)계산한다.
  * ``validator.py``: 결함위치탐지 데이터셋의 유효함을 검증한다.
  * ``machine_learning.py``: 최종 결함위치탐지 데이터셋으로 다층 퍼셉트론 (MLP: Multi-Layered Perceptron) 모델 학습과 추론을 수행한다.


# 4. Configuration 설정 방법
결함위치탐지 데이터셋 생성 작업을 수행하기 앞서 데이터셋 추출에 대한 구성요소를 ``./configs/config.json``, ``./configs/machines.json`` 파일에 그리고 대상 서브젝트에 대한 구성요소를 ``./subject/<subject-name>/`` 디렉토리에 설정해야 한다. 설정 방법은 4.1장과 4.2장에 설명한다.

## 4.1 실험 (FL 데이터셋 생성)에 대한 Configuration 설정 방법
### 4.1.2 ``./configs/config.json`` 파일 설정
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

### 4.1.3 ``./configs/config.json``의 설정 값 (변수) 설명
  * ``use_distributed_machines``: 분산 시스템 활용이 가능할 시``true``, 그렇지 않을 시 ``false``로 설정한다. ``true``로 설정할 ``./configs/machines.json`` 파일에 분산 시스템 정보를 입력해야 한다. 이에 대한 자세한 설명은 4.1.4장에서 볼 수 있다.
  * ``single_machine``: 현재 사용중인 서버의 정보를 설정해준다.
    * ``name``: 서버의 이름 혹은 ip 주소.
    * ``core``: 현재 사용중인 서버의 core 개수.
    * ``homedirectory``: 현재 사용중인 서버의 홈 디렉토리.
  * ``number_of_versions_to_check_for_usability``: 사용 가능성에 대한 검증을 거칠 버그 버전에 개수. 해당 변수는 결함위치탐지 데이터셋 생성의 2단계에서 사용되며 자세한 설명은 6.2장에서 볼 수 있다.
  * ``max_mutants``: 변이기반 데이터셋 생성 시 각 라인별 생성 할 변이의 최대 개수.
  * ``number_of_lines_to_mutation_test``: 변이기반 데이터셋 생성 시 변이 테스트를 수행 할 코드 라인의 최대 개수.
  * ``abs_path_to_gcovr_executable``: ``gcovr`` 실행 파일의 절대 주소. 이는 서브젝트의 커버리지 정보를 추출할 때 사용된다.
  * ``gcovr_version``: ``gcovr``의 버전.


### 4.1.4 ``./configs/machines.json`` 파일 설정
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

### 4.1.5 ``machines.json`` field aplanation
각 분산 시스템 (서버)의 정보를 위와 같은 형식으로, 서버 접속에 사용 할 명칭 혹은 ip 주소와 서버의 core 개수와 홈디렉토리로 구성된다.
  * ``cores``: 서버의 core 개수.
  * ``homedirectory``: 서버의 홈디렉토리.

추가적으로 현재 사용중인 서버 (main server)로부터 각 분산 시스템 (서버)에 자동 접속을 위해 공개키 (public key) 공유가 되어있어야 한다.


## 4.2 서브젝트에 대한 Configurations 설정 방법 (예시 기준: libxml2 서브젝트)
서브젝트에 해당되는 모든 정보 (서브젝트 리포지토리, 서브젝트 configurations, etc.)는 ``./subjects/`` 디렉토리에 위치 시킨다. 그러므로 사용자는 가장 먼저 ``./subjects/`` 디렉토리를 생성해야 한다. 서브젝트데 대한 configuration 설정하는 방법은 4.2.1장 부터 자세한 설명을 볼 수 있다 (설명은 ``libxml2`` 서브젝트 기준으로 예를 보인다).

### 4.2.1 서브젝트의 main 디렉토리 설정
  1. ``./subject/`` 디렉토리와 서브젝트 디렉토리 생성
      ```
      mkdir -p ./subjects/libxml2/
      ```

  2. 서브젝트의 리포지토리를 ``./subjects/libxml2/`` 위치에 복사, clone, 혹은 다운으로 내려받는다 (서브젝트 리포지토리 디렉토리의 명칭은 서브젝트 명칭과 동일하게 내려받는다).
      ```
      cd ./subjects/libxml2
      git clone <libxml2-link> libxml2
      ```

#### 4.2.2 서브젝트의 실제 버그 버전 설정 방법
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
          * ``target_code_file``: 서브젝트의 리포지토리 디렉토리부터 시작한 타깃 소스코드 파일 경로 (ex. ``libxml2/HTMLparser.c``)
          * ``buggy_code_file``: ``./real_world_buggy_versions/buggy_code_file/``에 저장한 ``<source-file>``의 이름.
          * ``buggy_lineno``: ``<source-file>``에 버기 라인이 위차하고 있는 라인 번호.

#### 4.2.3 서브젝트의 configurations 설정과 빌드, 정리 명령 실행 파일
  4. ``./configs/libxml2/configurations.json`` 파일은 서브젝트에 대한 configuration을 다음과 같은 형식으로 설정.
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
      * ``subject_name``: 서브젝트의 이름.
      * ``configuration_script_working_directory``: 서브젝트 configure 스크립트 (``configure_no_cov_script.sh`` and ``configure_yes_cov_script.sh``)가 실행 되어야 하는 경로.
      * ``build_script_working_directory``: 서브젝트의 빌드 스크립트 (``build_script.sh``)가 실행 되어야 하는 경로.
      * ``compile_command_path``: 서브젝트 빌드 후 생성 되는 ``compile_commands.json`` 파일의 경로.
      * ``test_case_directory``: 서브젝트 리포지토리에 테스트 케이스 실행 스크립트들이 저장된 디렉토리 (``testcases/``)의 경로. 사용자는 필수적으로 ``testcases/`` 명칭으로 디렉토리를 만든 후, 각 테스트 케이스를 실행하는 배시 스크립트(``<tc-id>.sh``)를 ``TC1.sh``, ``TC2.sh`` ... ``TC<N>.sh`` 형식으로 만들오 해당 디렉토리의 위치 시켜야 한다.
      * ``subject_language``: 해당 서브젝트의 프로그래밍 언어를 ``"C"`` 혹은 ``"CPP"``로 입력한다.
      * ``target_files``: 결함위치탐지 데이터셋 생성에 타깃으로 하는 소스코드 파일의 목록.
      * ``target_preprocessed_files``: 결함위치탐지 데이터셋 생성에 타깃으로 하는 소스코드 파일들의 전처리 파일의 목록.
      * ``real_world_buggy_versions``: 실제 버그 버전이 있을 시 ``true``, 실제 버그 버전이 없을 시 ``false``로 설정한다.
      * ``environment_settings``: 서브젝트 테스트 케이스를 실행 하기 위해 요구되는 환경 변수 설정 값.
        * ``needed``: 환경 변수 설정 필요 시 ``true`` 그렇지 않을 시 ``false``.
        * ``variables``: 테스트 케이스 실행에 필요한 환경 변수 설정 값의 목록.
      * ``cov_compiled_with_clang``: 서브젝트 빌드 명령이 ``clang`` 컴파일러를 사용 할 시 ``true``, ``gcc`` 컴파일러를 사용 할 시 ``false``.
      * ``gcovr_source_root``: 소스 코드 파일의 절대 경로. 이는 ``cov_compiled_with_clang`` 변수가 ``false``일 때 절대 경로로 설정해주며, ``cov_compiled_with_clang``이 ``true``일 때는 ``"None"``으로 설정해준다.
      * ``gcovr_object_root``: 소스 코드 파일의 object 파일이 저장 되는 절대 경로. 이는 ``cov_compiled_with_clang`` 변수가 ``false``일 때 절대 경로로 설정해주며, ``cov_compiled_with_clang``이 ``true``일 때는 ``"None"``으로 설정해준다.
      * ``test_initialization``: 서브젝트의 모든 테스트 케이스들이 공통으로 실행하는 초기화 코드 라인이 있을 시 해당 코드 라인들을 제외하기 위해 필요한 정보를 값을 갖는다.
        * ``status``: 서브젝트의 모든 테스트 케이스들이 공통으로 실행하는 초기화 코드 라인이 있을 시 ``true`` 값을 표기하며 그렇지 않을 시 ``false`` 값으로 표기한다.
        * ``init_cmd``: 초기화 코드 라인을 추출하기 위해 하나의 테스트 케이스 실행 스크립트의 경로 (서브젝트의 리포지토리 경로부터에서의 상대적 경로).
        * ``execution_path`` ``init_cmd``변수의 테스트 케이스 실행 스크립트가 실행 되어야하는 디렉토리 경로.
  5. ``./configs/libxml2/build_script.sh`` 이름으로 서브젝트 빌드 명령어로 실행 파일을 만든다. 이때 빌드가 실패할 때 1 값을, 성공할 시 0 값을 돌려주게 만든다.
      ```
      bear make -j20 runtest
      ```
  6. ``./configs/libxml2/clean_script.sh`` 이름으로 서브젝트 빌드 정리 명령어로 실행 파일을 만든다.
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


# 5. 결함위치탐지 데이터셋 생성 단계별 실행 방법

## 5.1 [1단계] 변이기반 버그 버전 생성
### 5.1.1 [1단계]에서 수행되는 작업
  1. **변이 생성**:
      * ``/subjects/libxml2/configuration.json`` configuration 설정 파일의 ``target_files`` 변수에 명시된 타깃 파일들에 대하여 변이들을 **생성** 한다. 생성된 변이 파일들은 자동으로 ``./out/<subject-name>/generated_mutants`` 디렉토리에 저장된다.
  2. **변이 버전 테스트**:
      * ``/subjects/libxml2/configuration.json`` configuration 설정 파일의 ``test_case_directory`` 변수에 명시된 디렉토리 경로에 담긴 테스트 케이스들의 배시 스크립트를 각 변이 버전에 실행 한다.
  3. **변이 버그 버전 저장**:
      * 각 변이 버그에 테스트 케이스들을 실행하여 1개 이상의 실패하는 테스트 케이스와 1개 이상의 패싱하는 테스트 케이스가 발생하는 버전은 ``./out/<subject-names>/buggy_mutants/`` 디렉토리에 자동으로 저장한다.

### 5.1.2 [1단계] 실행 방법
* 실행 명령어:
  ```
  $ time python3 collect_buggy_mutants.py --subject <subject-name> [--verbose]
  ```
* 옵션 설명:
  * ``--subject <subject-name>``: 실험 대상 서브젝트의 이름 (e.i., ``./subjects/``에 생성한 대상 서브젝트 디렉토리 이름과 동일)

## 5.2 [2단계] 버그 버전 사용 가능 여부 검증
### 5.2.1 [2단계]에서 수행되는 작업
  1. **변이 버그 버전 선택**:
      * ``./configs/config.json`` configuration 설정 파일의 ``number_of_versions_to_check_for_usability`` 변수에 설정된 값 만큼의 ``./out/<subject-name>/buggy_mutants/`` 디렉토리에 저장된 변이 버그 버전을 선택한다. (제한된 시간 조건으로 인해 사용자가 설정한 개수 만큼만 검증하여 데이터 추출에 사용되는 것이다)
  2. **실패 테스트 케이스 검증**:
      * 선택된 각 변이 버그 버전 별로 실패하는 테스트 케이스들을 실행하여 커버리즈 정보를 추출한다.
  3. **검증된 버그 버전 저장**:
      * 각 변이 버그 버전의 실패하는 테스트 케이스들의 커버리지 정보를 확인하여 사용가능 여부가 검증되면 ``./out/<subject-name>/usable_buggy_mutants/`` 디렉토리에 저장한다. 검증 조건은 다음과 같다:
        * 모든 실패하는 테스트 케이스는 버기 라인을 실행한다.
        * 변이 버그 버전은 1개 이상의 실패하는 테스트 케이스와 1개 이상의 패싱하는 테스트 케이스를 보유한다.

### 5.2.2 [2단계] 실행 방법
* 실행 명령어:
  ```
  $ time python3 select_usable_versions.py --subject <subject-name>
  ```
* 옵션 설명:
  * ``--subject <subject-name>``: 실험 대상 서브젝트의 이름 (e.i., ``./subjects/``에 생성한 대상 서브젝트 디렉토리 이름과 동일)

### 5.2.3 [2단계] 정상 작동 검증 방법
* 실행 명령어:
  ```
  $ python3 validator.py --subject <subject-name> --set-name <usable_buggy_versions-directory> --validate-usable-buggy-versions
  ```

* ``<usable_buggy_versions-directory>`` (입력: ``usable_buggy_mutants``) 디렉토리에 속한 각 변이 버그 버전 결과물에 대하여 다음 조건들의 만족 여부를 검증한다:
  * 버그 버전에 대한 기본 정보 (``target_code_file``,``buggy_code_file``,``buggy_lineno``)를 담는 csv 파일(``bug_info.csv``)의 생성 여부 검증
  * 실패와 패싱 테스트 케이스들의 목록 파일을 포함한 디렉토리(``testsuite_info/``)의 생성 여부 검증.
  * 버기 라인을 포함한 소스 코드 파일을 포함한 디렉토리(``buggy_code_file/``)의 생성 여부 검증


## 5.3 [3단계] 결함위치탐지 데이터셋 생성에 필요한 사전 데이터 추출
### 5.3.1 [3단계]에서 수행되는 작업
  1. **사정 데이터 추출**:
      * ``./out/<subject-name>/usable_buggy_mutants/`` 디렉토리에 저장된 각 버그 버전에 대해 사전 데이터를 추출하여 ``./out/<subject-name>/prerequisite_data/`` 디렉토리에 저장한다. 
      * 또한, ``/subjects/libxml2/configuration.json``의 ``real_world_buggy_versions`` 변수로 실제 버그 사용 여부에 따라, ``true``일 시 ``./subjects/libxml2/real_world_buggy_versions/`` 디렉토리에 저장된 실제 버그 버전도 포함하여 사전 데이터를 추출하여 저장한다.
      * 사전 데이터는 다음과 같은 정보를 의미한다:
        * 후처리 된 커버리지 정보 (CSV format)
        * 라인-함수 매핑 정보 (JSON format)
        * 실패한 테스트 케이스들이 실행한 라인 정보 (JSON format)
        * 패싱한 테스트 케이스들이 실행한 라인 정보 (JSON format)
        * 우연히 통과한 테스트 케이스들이 실행한 라인 정보 (Json format)
        * 우연히 실행 테스트 케이스들의 목록

### 5.3.2 [3단계] 실행 방법
* 실행 명령어:
  ```
  $ time python3 prepare_prerequisites.py --subject <subject-name> --target-set-name <usable_buggy_versions-directory>
  ```
* 옵션 설명:
  * ``--subject <subject-name>``: 실험 대상 서브젝트의 이름 (e.i., ``./subjects/``에 생성한 대상 서브젝트 디렉토리 이름과 동일)
  * ``--target-set-name <usable_buggy_versions-directory>``: 사전 데이터를 추출하고자 하는 버그 버전들이 저장된 디렉토리 이름. (입력: ``usable_buggy_versions``)

### 5.3.3 [3단계] 정상 작동 검증 방법
* 실행 명령어:
  ```
  $ python3 validator.py --subject <subject-name> --set-name <prerequisite_data-directory> --validate-prerequisite-data
  ```
* ``<prerequisite_data-directory>`` (입력: ``prerequisite_data``) 디렉토리에 속한 각 버그 버전 결과물에 대하여 다음 조건들의 만족 여부를 검증한다:
  * 버기 라인의 고유 키 값 정보가 담긴 txt 파일(``buggy_line_key.txt``)의 생성 여부 검증
  * 커버러지의 개요 정보가 담긴 csv 파일(``coverage_summary.csv``)의 생성 여부 검증
  * 각 테스트 케이스 별 라인 커버러지 정보가 담긴 csv 파일(``postprocess_coverage.csv``)의 생성 여부 검증
  * ``postprocess_coverage.csv`` 파일 데이터상 실패하는 테스트 케이스들의 버기 라인 실행 여부 검증
  * 실패 테스트 케이스들의 라인 커버리지 정보가 담긴 json 파일(``lines_executed_by_failing_tc.json``)의 생성 여부 검증
  * 각 라인 별 함수 매핑 정보가 담긴 파일(``line2function.json``)의 생성 여부 검증

### 5.3.4 [3단계] 사전 데이터의 통계 자료 계산
* 실행 명령어:
  ```
  $ python3 analyzer.py --subject <subject-name> --set-name <prerequisite_data-directory> --output-csv <prerequisite_data-directory>-tc-stats --prerequisite-data --removed-initialization-coverage
  ```
* ``<prerequisite_data-directory>`` (입력: ``prerequisite_data``) 디렉토리에 속한 각 버그 버전 결과물로 부터 각종 정보를 계산하여 ``./statistics/<subject-name>/`` 디렉토리에 ``<prerequisite_data-directory>-tc-stats.csv`` 이름으로 저장된다.
* 사전 데이터의 통계 자료는 다음과 같은 정보들을 포함한다:
  * 테스트 케이스들의 개수 (i.e., 실패, 패싱, 우연히 패싱하는 테스트 케이스) 정보
  * 실패하는 테스트 케이스들이 실행하는 함수와 라인 개수 정보

## 5.4 [4단계] 변이기반 (MBFL: Mutation-Based) 데이터셋 추출
### 5.4.1 [4단계]단계에서 수행되는 작업
  1. **변이 생성**:
      * 각 버그 버전 별로 ``./configs/config.json`` configuration 설청 파일의 ``number_of_lines_to_mutation_test`` 변수에 설정된 값 만큼의 라인을 선택하여, 각 라인별 ``max_mutants`` 변수에 설정된 값 만큼의 변이를 생성한다.
  2. **변이기반 테스팅**:
      * 각 버그 버전에 생성된 변이의 적용과 테스트 케이스들을 실행하여 변이기반 테스팅을 수행한다.
  3. **변이기반 데이터 저장**:
      * 변이기반 테스팅을 끝난 후 변이기반 데이터 결과물을 ``./out/<subject-name>/mbfl_features/`` 디렉토리에 저장한다.


### 5.4.2 [4단계] 실행 방법
* 실행 명령어:
  ```
  $ time python3 extract_mbfl_features.py --subject <subject-name> --target-set-name <prerequisite_data-directory> --trial <trial-name> [--exclude-init-lines] [--parallel-cnt <int>] [--dont-terminate-leftovers]
  ```
* 옵션 설명:
  * ``--subject <subject-name>``: 실험 대상 서브젝트의 이름 (e.i., ``./subjects/``에 생성한 대상 서브젝트 디렉토리 이름과 동일)
  * ``--target-set-name <prerequisite_data-directory>``: 변이기반 데이터셋 추출하고자 하는 버그 버전들이 저장된 디렉토리 이름. (입력: ``prerequisite_data``)
  * ``--trial <trial-name>``: 실험 trial 이름 (ex. trial1)
  * ``--exclude-init-lines``: 해당 옵션을 키게 되면, 테스트 환경 초기화할 때 실행 되는 라인을 변이기반 테스팅 대상 라인에서 제외한다.
  * ``--prallel-cnt <int>``: 변이기반 데이터셋 추출작업을 <int> 개수 만큼 병령적으로 수행하는 옵션.
  * ``--dont-terminate-leftovers``: 해당 옵션을 키게 되면, 모든 버그버전의 변이기반 데이터셋 추출 작업이 끝날 때 까지 기다린다.


### 5.4.3 [4단계] 정상 작동 검증 방법
* 실행 명령어:
  ```
  $ python3 validator.py --subject <subject-name> --set-name <mbfl_features-directory> --validate-mbfl-features --trial <trial-name>
  ```
* ``<mbfl_features-directory>`` (입력: ``mbfl_features``) 디렉토리에 속한 각 버그 버전 결과물에 대하여 다음 조건들의 만족 여부를 검증한다:
  * 변이기반 데이터셋 csv 파일(``mbfl_features.csv``)의 생성 여부 검증
  * ``mbfl_features.csv`` 변이기반 데이터셋 csv 파일에 1개의 버기 라인 존재 여부 검증
  * 변이기반 테스팅 수행에 활용된 변이 정보 csv 파일(``selected_mutants.csv``)의 생성 여부 검증
  * 변이기반 테스팅 결과 csv 파일(``mutation_testing_results.csv``)의 생성 여부 검증

### 5.4.4 [4단계] 변이기반 데이터셋의 정확도 계산 결과 추출 방법
* 실행 명령어:
```
$ python3 ranker.py --subject <subject-name> --set-name <mbfl_features-directory> --output-csv <mbfl_features-directory>-rank-stats --mbfl-features --trial <trial-name> [--no-ccts]
```
* ``<mbfl_features-directory>`` (입력: ``mbfl_features``) 디렉토리에 속한 각 버그 버전의 변이기반 데이터로부터 버기 함수 탐지 정확도를 계산한다. 정확도 결과는 ``./statistics/<subject-name>/`` 디렉토리에 ``<mbfl_features-directory>-rank-stats.csv`` 이름으로 저장된다.
* 옵션 설명:
  * ``--no-ccts``: 해당 옵션을 키게 되면, 우연히 통과한 테스트 케이스들을 제외한 데이터셋을 가지고 변이기반 데이터를 평가한다.



## 5.5 [5단계] 스펙트럼기반 (SBFL: Spectrum-Based) 데이터셋 추출
### 5.5.1 [5단계]에서 수행되는 작업
  1. **스펙트럼기반 데이터 생성 및 정리**:
      * 각 버그 버전 별 ``postprocess_coverage.csv``의 커버리지 정보를 활용하여 스펙트럼기반 데이터 생성하고 ``./out/<subject-name>/sbfl_features/`` 디렉토리에 저장한다.

### 5.5.2 [5단계] 실행 방법
* 실행 명령어:
  ```
  $ time python3 extract_sbfl_features.py --subject <subject-name> --target-set-name <mbfl_features-directory>
  ```
* 옵션 설명:
  * ``--subject <subject-name>``: 실험 대상 서브젝트의 이름 (e.i., ``./subjects/``에 생성한 대상 서브젝트 디렉토리 이름과 동일)
  * ``--target-set-name <mbfl_features-directory>``: 스펙트럼기반 데이터셋 추출하고자 하는 버그 버전들이 저장된 디렉토리 이름. (입력: ``mbfl_features``)

### 5.5.3 [5단계] 정상 작동 검증 방법
* 실행 명령어:
  ```
  $ python3 validator.py --subject <subject-name> --set-name <sbfl_features-directory> --validate-sbfl-features
  ```
* ``<sbfl_features-directory>`` (입력: ``sbfl_features``) 디렉토리의 각 버그 버전 결과물에 대하여 다음 조건들의 만족 여부를 검증한다:
  * 스펙트럼기반 데이터셋 csv 파일(``sbfl_features.csv``)의 생성 여부 검증

### 5.5.4 [5단계] 스펙트럼기반 데이터셋의 정확도 계산 결과 추출 방법
* 실행 명령어:
  ```
  $ python3 ranker.py --subject <subject-name> --set-name <sbfl_features-directory> --output-csv <sbfl_features-directory>-rank-stats --sbfl-features [--no-ccts]
  ```
* ``<sbfl_features-directory>`` (입력: ``sbfl_features``) 디렉토리에 속한 각 버그 버전의 스펙트럼기반 데이터로부터 버기 함수 탐지 정확도를 계산한다. 정확도 결과는 ``./statistics/<subject-name>`` 디렉토리에 ``<sbfl_features-directory>-rank-stats.csv`` 이름으로 저장된다.
* 옵션 설명:
  * ``--no-ccts``: 해당 옵션을 키게 되면, 우연히 통과한 테스트 케이스들을 제외한 데이터셋을 가지고 스펙트럼기반 데이터를 평가한다.

## 5.6 [6단계] 변이기반과 스펙트럼기반 데이터 병합하여 최종 결함위치탐지 데이터셋 생성
### 5.6.1 [6단계]에서 수행되는 작업
  1. **최종 결함위치탐지 데이터셋 생성**:
      * 변이기반과 스펙트럼기반 데이터셋을 병합하여 최종 결함위치탐지 데이터셋을 생성하고 ``./out/<subject-name>/FL-dataset-<subject-name/`` 디렉토리에 저장한다.

### 5.6.2 [6단계] 실행 방법
* 실행 명령어:
  ```
  $ python3 reconstructor.py --subject <subject-name> --set-name <sbfl_features-directory> --combine-mbfl-sbfl --combining-trials <trial-name> [--no-ccts] [--done-remotely]
  ```
* 옵션 설명:
  * ``--subject <subject-name>``: 실험 대상 서브젝트의 이름 (e.i., ``./subjects/``에 생성한 대상 서브젝트 디렉토리 이름과 동일)
  * ``--target-set-name <sbfl_features-directory>``: 스펙트럼기반 데이터셋 추출하고자 하는 버그 버전들이 저장된 디렉토리 이름. (입력: ``sbfl_features``)
  * ``--combine-mbfl-sbfl``: 변이기반과 스펙트럼기반 데이터 병합하는 옵션.
  * ``--combining-trials [<trial-name> ...]``: 실험 trial 이름 (ex. trial1)
  * ``--no-ccts``: 해당 옵션을 키게 되면, 우연히 통과한 테스트 케이스들을 제외한 변이기반과 스펙트럼기반 데이터셋을 병합한다.
  * ``--done-remotely``: 해당 옵션을 키게 되면, 변이기반 데이터셋 추출에 활용된 변이들을 분산 시스템으로부터 내려받는다.

### 5.6.3 [6단계] 정상 작동 검증 방법
* 실행 명령어:
  ```
  $ python3 validator.py --subject <subject-name> --set-name FL-dataset-<subject-name> --validate-fl-features
  ```
* ``FL-dataset-<subject-name>``, 즉, 최종 결함위치탐지 데이터셋에 대하여 다음 조건들의 만족 여부를 검증한다:
  * 각 버그 버전의 ``<bug-id>.fl_features.csv`` 파일에 단 1개의 버기 라인의 존재 여부를 검증한다.
  * 각 버그 버전의 결함위치탐지 데이터의 스펙트럼 정보 (ep, ef, np, nf)의 합이 활용된 테스트 케이스의 개수와 동일한 것을 검증한다.
  * 각 버그 버전의 실패하는 테스트 케이스들이 버기 라인을 실행하는 것을 검증한다.
  * 각 버그 버전의 변이기반 데이터로부터 Metallaxis와 MUSE 의심도 값이 정상적 계산 여부를 검증한다.
  * 각 버그 버전의 변이 코드 (1개의 라인)이 실제 버그 소스 코드 파일에 위치하고 있는 것을 검증한다.

<!-- # 6. 다층 퍼셉트론 모델에 결함위치탐지 데이터셋 학습과 추론 방법
다층 퍼셉트론 모델 학습과 추론을 위한 결함위치탐지 데이터셋은 ``./out/<subject-name>/`` 디렉토리에 위치해야한다. 모델 학습과 추론은 5장에서 생성한 결함위치탐지 데이터셋을 사용한다.

## 6.1 결함위치탐지 데이터셋 후처리
* 실행 명령어:
  ```
  $ python3 machine_learning.py --subject2setname-pair <subject-name>:<fl-dataset-directory> --postprocess-fl-features
  ```

## 6.2 학습/검증/테스트 데이터로 분할 후 모델 학습
* 실행 명령어:
  ```
  $ python3 machine_learning.py --subject2setname-pair <subject-name>:<fl-dataset-directory> --train --project-name ML-<date>-<subject-name>-<version> --train-validate-test-ratio 6 1 3 --random-seed 42 --epoch 20 --batch-size 1024 --learning-rate 0.001 --dropout 0.2 --model-shape 35 64 32 1
  ```

## 6.3 학습 후 모델 추론
* 실행 명령어:
  ```
  $ python3 machine_learning.py --subject2setname-pair <subject-name>:<fl-dataset-directory> --inference --project-name ML-<date>-<subject-name>-<version> --inference-name infer-<subject-name>-<version>
  ```

## 6.4 결함위치탐지 데이터로부터 실제 버그만 분할 처리
* 실행 명령어:
  ```
  $ python3 machine_learning.py --subject2setname-pair <subject-name>:<fl-dataset-directory> --part-real-world-bugs --real-world-bugs [<str> ...]
  ``` -->

---
마지막 업데이트 2024년 11월 06일
