# NSFW (CPP) 프로젝트의 결함 위치 탐지 (FL: Fault Localization) 데이터셋


## 1. 데이터셋 소개
본 데이터셋은 NSFW (CPP언어) LIGNex1의 프로그램을 대상으로 결함 위치 탐지 모델에 활용될 수 있는 학습 데이터를 제공합니다. 이 데이터셋은 프로그램의 동적 특성을 분석하여 스펙트럼 기반 (SBFL: Spectrum-Based Fault Localization) 및 변이 기반 (MBFL: Mutation-Based Fault Localization) 특징 데이터를 포함하고 있습니다.


## 2. FL 데이터셋 구축에 사용된 NSFW 파일 규모 요약
* NSFW_cfg
    * 소스 코드 파일 개수: 6개
    * 함수 개수: 163개
    * 소스 코드 라인 개수: 1,103줄
* NSFW_file
    * 소스 코드 파일 개수: 6개
    * 함수 개수: 178개
    * 소스 코드 라인 개수: 954줄
* NSFW_thread
    * 소스 코드 파일 개수: 12개
    * 함수 개수: 222개
    * 소스 코드 라인 개수: 1,084

### 2.1 데이터셋 파일 개수
* 총 파일 개수: 582,261개

홈디렉토리의 파일 및 디렉토리 | 파일 개수
--- | ---
``buggy_code_file_per_bug_version/`` | 402
``buggy_line_key_per_bug_version/`` | 378
``bug_version_mutation_info.csv`` | 1
``document-NSFW_cpp.md`` | 1
``FL_features_per_bug_version/`` | 378
``FL_features_per_bug_version_with_susp_scores/`` | 378
``generated_mutants_for_mbfl_per_bug/`` | 579,207
``NSFW_cfg.zip`` | 1
``NSFW_file.zip`` | 1
``NSFW_thread.zip`` | 1
``postprocessed_coverage_per_bug_version/`` | 378
``susp_score.py`` | 1
``test_case_info_per_bug_version/`` | 1,134

## 3. 데이터셋 구조
### 3.1 디렉토리 구조
* 데이터 구조
    * ``buggy_code_file_per_bug_version/:`` 각 버그 버전에 대한 버그가 있는 소스 코드 파일
        * ``└── original_version/``: 버그가 없는 원본 소스 코드 파일들이 포함된 디렉토리
    * ``buggy_line_key_per_bug_version/``: 각 버그 버전의 버기 라인을 식별하는 고유 키 값
    * ``bug_version_mutation_info.csv``: 각 버그 버전에 생성된 인공 버그의 변형 정보
    * ``document-NSFW_cpp.md``: 데이터셋의 상세 내용을 설명하는 문서
    * ``FL_features_per_bug_version/``: 버그 버전 별로 SBFL과 MBFL 특징 정보를 포함한 학습 데이터 **(학습 데이터로 사용)**
    * ``FL_features_per_bug_version_with_susp_scores/``: 버그 버전 별로 SBFL과 MBFL 특징 정보에 더해, Metallaxis와 MUSE 공식에 적용하여 계산된 읨심도 점수를 포함하는 데이터 파일 (MBFL 의심도 점수 검증 할 때 사용)
    * ``generated_mutants_for_mbfl_per_bug/``: MBFL 특징 추출을 위해 각 버그 버전 별 생성된 변이들의 소스 파일
    * ``NSFW_cfg.zip``: NSFW_cfg 프로젝트 리포지토리 압축 파일
    * ``NSFW_file.zip``: NSFW_file 프로젝트 리포지토리 압축 파일
    * ``NSFW_thread.zip``: NSFW_thread 프로젝트 리포지토리 압축 파일
    * ``postprocessed_coverage_per_bug_version/``: 각 버그 버전의 테스트 케이스들의 커버리지 정보
    * ``susp_score.py``: 하나의 버그 버전에 대한 Metallaxis와 MUSE 의심도를 계산해주는 도구
    * ``test_case_info_per_bug_version/``: 각 버그 버전 별로 사용된 테스트 케이스 분류 정보
        * ``├── ccts.txt``: 버기 라인을 실행 했으나 우연히 통과한 (coincidentally correct)  테스트 케이스
        * ``├── crashed_tcs.txt``: 테스트 케이스 실행 후 프로그램 강제 종료 발생하는 테스트 케이스
        * ``├── excluded_failing_tcs.txt``: 동적 특징 추출에 제외된 실패 (failing) 테스트 케이스
        * ``├── excluded_passing_tcs.txt``: 동적 특징 추출에 제외된 통과 (passing) 테스트 케이스
        * ``├── failing_tcs.txt``: 동적 특징 추출에 사용된 실패 (failing) 테스트 케이스
        * ``└── passing_tcs.txt``: 동적 특징 추출에 사용된 통과 (passing) 테스트 케이스
    ```
    fl_dataset-NSFW_cpp-240819-v1/
        ├── buggy_code_file_per_bug_version/
        ├── buggy_line_key_per_bug_version/
        ├── bug_version_mutation_info.csv
        ├── document-NSFW_cpp.md
        ├── FL_features_per_bug_version/
        ├── FL_features_per_bug_version_with_susp_scores/
        ├── generated_mutants_for_mbfl_per_bug/
        ├── NSFW_cfg.zip
        ├── NSFW_file.zip
        ├── NSFW_thread.zip
        ├── postprocessed_coverage_per_bug_version/
        ├── susp_score.py
        └── test_case_info_per_bug_version/
    ```


## 4. 버그 버전 정보
### 4.1 버그 개수
유형 | 개수
--- | ---
NSFW_cfg 버그 | 207개
NSFW_file 버그 | 143개
NSFW_thread 버그 | 28개
총 버그 | 378개

### 4.3 인공 버그 (총 146개)
* ``bug_version_mutation_info.csv`` 파일에는 각 인공 버그의 상세 정보가 기록되어 있습니다. 이 파일은 각 버그 버전에 대한 다음 정보를 포함합니다:
    * 버그 버전
    * 변형 소스 코드 파일 이름
    * 변형 소스 코드 라인 위치 (Line#, Col#)
    * 변형 연산자 (Mutation Operator)
    * 변형 전 소스 코드 정보 (Before Mutation)
    * 변형 후 소스 코드 정보 (After Mutation)


## 5. 검증된 데이터와 검증 방법
* ``FL_features_per_bug_version/`` 디렉토리: 버그 버전 별 결함 위치 탐지 데이터셋
    * 각 CSV 파일은 ``bug`` 열의 값이 ``1``인 행은 유일하게 한 하나만 존재하는지 검증합니다.
    * 스펙트럼 기반 특징 데이터 (``ep``, ``ef``, ``np``, ``nf``)의 합계가 통과와 실패하는 테스트 케이스의 총 개수와 일치하는지 검증합니다.
    * 변이 기반 특징 데이터로부터 **Metallaxis**와 **MUSE** 공식에 올바르게 적용 가능한것을 검증합니다.
* ``buggy_code_file_per_bug_version/`` 디렉토리: 버그 버전 별 버그가 포함 된 소스 코드 파일
    * 인공적으로 생성된 버그(변형)가 각 버그 버전의 소스 코드 파일에 지정된 위치에 올바르게 삽입되었는지 검증합니다.
* ``test_case_info_per_bug_version/`` 디렉토리: 각 버그 버전 별 실패한 테스트 케이스 정보
    * 각 버그 버전 별 실패(failing) 테스트 케이스가 해당 버그에서 버그가 있는 코드 라인을 실행하였는지 검증합니다.


## 6. 모델 학습용 데이터셋 특징 (총 48개 열)
* 변이 기반 특징의 열 개수는 각 라인 별 최대 변이 개수, ``# of mutants``에 따라 변동 될 수 있습니다.
* 현재 데이터셋에서는 라인 별 최대 변이 개수는 20개로 설정 되어 구축되었습니다.

### 6.1 각 라인 별 고유 키 (``key`` 열):
* 이 열은 ``<소스 코드 파일>#<함수명>#<라인 번호>`` 형식으로 각 소스 코드 라인의 고유 식별자를 기록합니다.

### 6.2 버기 라인 여부 (``bug`` 열):
* ``bug`` 열의 값이 ``1``이면 해당 라인은 버기 라인임을 나타냅니다.
* ``bug`` 열의 값이 ``0``이면 해당 라인은 정상 라인임을 나타냅니다.

### 6.3 스펙트럼 기반 특징 (SBFL, 총 4개 열):
* ``ep``: 해당 라인을 실행하고 통과한(pass)한 테스트 케이스의 개수
* ``ef``: 해당 라인을 실행하고 실패한(fail)한 테스트 케이스의 개수
* ``np``: 해당 라인을 실행하지 않고 통과한(pass)한 테스트 케이스의 개수
* ``nf``: 해당 라인을 실행하지 않고 실패한(fail)한 테스트 케이스의 개수

### 6.4 변이 기반 특징 (MBFL, 총 42개 열):
* 변이 기반 특징
    * ``# of totfailed_TCs``: $totalFailing_\text{TCs}$
    * ``# of mutants``: 각 라인별 생성된 변이의 최대 개수 (설정 값)
    * ``m<i>:f2p``: $|f_P(s) \cap p_m|$ (<$i$>는 $i$번째 변이 $m$를 말한다)
    * ``m<i>:p2f``: $|p_P(s) \cap f_m|$ (<$i$>는 $i$번째 변이 $m$를 말한다)
* 수실 추가 설명:
    * $totalFailing_\text{TCs}$: 버그 버전 프로그램에서 fail한 테스트 케이스의 개수
    * $|f_P(s) \cap p_m|$: 버그 버전 프로그램 $P$에서 라인 $s$를 실행하고 fail하던 테스트 케이스가 변이 $m$이 있는 프로그램에서 pass하는 테스트 케이스의 개수
    * $|p_P(s) \cap f_m|$: 버그 버전 프로그램 $P$에서 라인 $s$를 실행하고 pass하던 테스트 케이스가 변이 $m$이 있는 프로그램에서 fail하는 테스트 케이스의 개수
    * ``m<i>:f2p``와 ``m<i>:p2f`` 값이 ``-1``인 변이는 최종 의심도 계산에 제외합니다.



## 7. 변이 기반 라인의 의심도 계산
### 7.1 변이 기반 의심도 공식 설명
* **Metallaxis**
    * $\max_{m \in \text{mut}_\text{killed}(s)} \frac{|f_P(s) \cap p_m|}{\sqrt{totalFailing_\text{TCs} \times (({|f_P(s) \cap p_m|}) + ({|p_P(s) \cap f_m|}) )}}$

* **MUSE**
    * $\frac{1}{{(|\text{mut}(s)|+1)(f2p+1)}} \times \sum_{m \in \text{mut}(s)} \left( |f_P(s) \cap p_m| \right) - \frac{1}{{(|\text{mut}(s)|+1)(p2f+1)}} \times \sum_{m \in \text{mut}(s)} \left( |p_P(s) \cap f_m| \right)$


* 수식 추가 설명:
    * $\text{mut}_\text{killed}(s)$: 라인 $s$에 생성된 변형들 중 죽은 변형들의 개수
    * $\text{mut}(s)$: 라인 $s$에 활용된 변형들의 집합
    * $f_P(s) (\text{or } p_P(s))$: 대상 프로그램 $P$에서 라인 $s$를 실행하고 fail (or pass)하는 테스트 케이스들의 집합
    * $f_m (\text{or }p_m)$: 변형 $m$에 대해 fail (or pass)하는 테스트 케이스들의 집합
    * $f2p (\text{or }p2f)$: 대상 프로그램 $P$의 모든 변형들에 대해서 fail에서 pass (or pass에서 fail)로 바뀐 테스트 케이스들의 개수


### 7.2 ``susp_score.py`` 사용 방법
* 해당 도구는 하나의 버그 버전의 결함 위치 탐지 데이터를 주고 Metallaxis와 MUSE 의심도 점수를 계산해주는 도구입니다.
* 입력: 결함 위치 탐지 데이터 CSV 파일 (절대 경로)
* 출력: 라인 별 Metallaxis와 MUSE 의심도 점수가 담긴 ``susp_score.csv`` 파일
* 사용 명령 예시:
    ```
    ./susp_score.py -f /home/foo/fl_dataset-240419-v1/FL_features_per_bug_version/bug1.fl_features.csv
    ```



## 8. 테스트 케이스 소스 코드 정보
### 8.1 테스트 케이스 유추 방법 (NSFW_cfg, NSFW_file, NSFW_thread 대상 서브젝트)
1. ``<대상 서브젝트>.zip`` 압축 파일 풀어 <대상 서브젝트> 리포지토리 도출
2. ``<대상 서브젝트>/linux_cfg/linux_cmake/Testsuite`` 디렉토리에 ``tcs_DB.csv`` 파일을 참고
    * ``tcs_DB.csv``에 테스트 케이스 별 특징 구성:
        * ``<test_code_filename>``: 테스트 함수 위치 소스코드 파일
        * ``<tc_func_name>``: 테스트 케이스 함수 이름
3. ``tcs_DB.csv``에 담긴 정보로 부터 ``<test_code_filename>`` 소스 코드에서 테스트 케이스의 실행 함수 유추



## 9. 데이터셋의 결함 위치 탐지 정확도 평가 (총 378개 버그 버전)
* 각 결함 위치 탐지 공식 별 **함수 단위**로 버기 함수 탐지 정확도 결과

### 9.1 변이 기반 정확도 (MBFL)
MBFL 공식 | ``acc@5`` 버그 개수 | ``acc@5`` 정확도 백분율 | ``acc@10`` 버그 개수 | ``acc@10`` 정확도 백분율
--- | --- | --- | --- | --- |
Metallaxis | 280 | 74.07% | 281 | 74.34%
MUSE | 280 | 74.07% | 281 | 74.34%

### 9.2 스펙트럼 기반 정확도 (SBFL)
SBFL 공식 | ``acc@5`` 버그 개수 | ``acc@5`` 정확도 백분율 | ``acc@10`` 버그 개수 | ``acc@10`` 정확도 백분율
--- | --- | --- | --- | --- |
Binary | 14 | 3.70% | 39 | 10.32%
GP13 | 160 | 42.33% | 222 | 58.73%
Jaccard | 160 | 42.33% | 222 | 58.73%
Naish1 | 160 | 42.33% | 222 | 58.73%
Naish2 | 160 | 42.33% | 222 | 58.73%
Ochiai | 160 | 42.33% | 222 | 58.73%
Russel+Rao | 14 | 3.70% | 39 | 10.32%
Wong1 | 14 | 3.70% | 39 | 10.32%


