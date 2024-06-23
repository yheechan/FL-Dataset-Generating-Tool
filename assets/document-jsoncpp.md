# JsonCpp 오픈 소스 프로젝트의 오류 탐지 (FL: Fault Localization) 데이터셋


## 1. 데이터셋 소개
본 데이터셋은 JsonCpp 오프 소스 프로젝트를 대상으로 오류 탐지 모델에 활용될 수 있는 학습 데이터를 제공합니다. 이 데이터셋은 프로그램의 동적 특성을 분석하여 스펙트럼 기반 (SBFL: Spectrum-Based Fault Localization) 및 변이 기반 (MBFL: Mutation-Based Fault Localization) 특징 데이터를 포함하고 있습니다.


## 2. JsonCpp 프로젝트 규모 요약
* 소스 코드 파일 개수: 8개
* 함수 개수: 363개
* 소스 코드 라인 개수: 약 4000줄


## 3. 데이터셋 구조

### 3.1 디렉토리 구조
* ``buggy_code_file_per_bug_version/:`` 각 버그 버전에 대한 버그가 있는 소스 코드 파일
    * ``buggy_code_file_per_bug_version/original_version/``: 버그가 없는 원본 소스 코드 파일과 테스트 케이스 소스 코드가 포함된 디렉토리
* ``buggy_line_key_per_bug_version/``: 각 버그 버전의 버기 라인을 식별하는 고유 키 값
* ``bug_version_mutation_info.csv``: 각 버그 버전에 생성된 인공 버그의 변형 정보
* ``document.md``: 데이터셋의 상세 내용을 설명하는 문서
* ``FL_features_per_bug_version/``: 버그 버전 별로 SBFL과 MBFL 특징 정보를 포함한 학습 데이터 **(학습 데이터로 사용)**
* ``FL_features_per_bug_version_with_susp_scores/``: 버그 버전 별로 SBFL과 MBFL 특징 정보에 더해, Metallaxis와 MUSE 공식에 적용하여 계산된 읨심도 점수를 포함하는 데이터 파일 (MBFL 의심도 점수 검증 할 때 사용)
* ``postprocessed_coverage_per_bug_version/``: 각 버그 버전의 테스트 케이스들의 커버리지 정보
* ``susp_score.py``:하나의 버그 버전에 대한 Metallaxis와 MUSE 의심도를 계산해주는 도구
* ``test_case_info_per_bug_version/``: 각 버그 버전 별로 사용된 테스트 케이스 분류 정보 (통과(pass), 실패(fail), 우연히 통과한(coincidentally correct) 테스트 케이스)

    ```
    fl_dataset-240419-v1/
        ├── buggy_code_file_per_bug_version
        ├── buggy_line_key_per_bug_version
        ├── bug_version_mutation_info.csv
        ├── FL_features_per_bug_version
        ├── FL_features_per_bug_version_with_susp_scores
        ├── postprocessed_coverage_per_bug_version
        ├── susp_score.py
        └── test_case_info_per_bug_version
    ```


## 4. 버그 버전 정보
### 4.1 버그 개수
유형 | 개수
--- | ---
실제 버그 | 3개
인공 버그 | 162개
총 버그 | 165개

### 4.2 실제 버그 (총 3개)
버기 버전 | 출처 | 소스 코드 파일  | buggy line # | bug type
--- | --- | --- | --- | ---
bug1 | [github issue #1121](https://github.com/open-source-parsers/jsoncpp/issues/1121) | json_reader.cpp | 467 | assertion failure
bug2 | [ossfuzz #18147](https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=18147&q=jsoncpp&can=1&sort=-summary) | json_reader.cpp |  1279 | heap overflow
bug3 | [ossfuzz #21916](https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=21916&q=jsoncpp&can=1) | json_reader.cpp | 1628 | integer overflow

### 4.3 인공 버그 (총 162개)
* ``bug_version_mutation_info.csv`` 파일에는 각 인공 버그의 상세 정보가 기록되어 있습니다. 이 파일은 각 버그 버전에 대한 다음 정보를 포함합니다:
    * 버그 버전
    * 변형 소스 코드 파일
    * 변형 소스 코드 라인 번호
    * 변형 연산자
    * 변형 전 소스 코드
    * 변형 후 소스 코드


## 5. 검증된 데이터와 검증 방법
* ``FL_features_per_bug_version/`` 디렉토리: 버그 버전 별 오류 탐지 데이터셋
    * 각 CSV 파일은 ``bug`` 열의 값이 ``1``인 행은 유일하게 한 하나만 존재하는지 검증합니다.
    * 스펙트럼 기반 특징 데이터 (``ep``, ``ef``, ``np``, ``nf``)의 합계가 실패(failing) 및 통과(passing) 테스트 케이스의 총수와 일치하는지 검증합니다. 버기 라인을 실행했으나 우연히 통과하는 테스트 케이스는 제외합니다.
    * 변이 기반 특징 데이터로부터 **Metallaxis**와 **MUSE** 공식에 올바르게 적용 가능한것을 검증합니다.
* ``buggy_code_file_per_bug_version/`` 디렉토리: 버그 버전 별 소스 코드 파일
    * 인공적으로 생성된 버그(변형)가 각 버그 버전의 소스 코드 파일에 지정된 위치에 올바르게 삽입되었는지 검증합니다.
* ``test_case_info_per_bug_version/`` 디렉토리: 각 버그 버전 별 실패한 테스트 케이스 정보
    * 각 버그 버전 별 실패(failing) 테스트 케이스가 해당 버그에서 버그가 있는 코드 라인을 실행하였는지 검증합니다.


## 6. 모델 학습용 데이터셋 특징 (총 32개 열)
* 변이 기반 특징의 열 개수는 각 라인 별 최대 변이 개수, ``# of mutants``에 따라 변동 될 수 있습니다.
* 현재 데이터셋에서는 라인 별 최대 변이 개수는 12개로 설정 되어 구축되었습니다.

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

### 6.4 변이 기반 특징 (MBFL, 총 26개 열):
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
* 해당 도구는 하나의 버그 버전의 오류 탐지 데이터를 주고 Metallaxis와 MUSE 의심도 점수를 계산해주는 도구입니다.
* 입력: 오류 탐지 데이터 CSV 파일 (절대 경로)
* 출력: 라인 별 Metallaxis와 MUSE 의심도 점수가 담긴 ``susp_score.csv`` 파일
* 사용 명령 예시:
    ```
    ./susp_score.py -f /home/foo/fl_dataset-240419-v1/FL_features_per_bug_version/bug1.fl_features.csv
    ```



## 8. 테스트 케이스 소스 코드 정보

### 8.1 테스트 케이스 기록 방법
* 각 버그 버전 별 테스트 케이스는 ``test_case_info_per_bug_version/<bug version>/`` 디렉토리에 기록한다.
* 테스트 케이스는 다음 세 가지 유형으로 뷴류되어 기록됩니다 (tc_id와 tc_name으로 기록한다):
    * 실패 테스트 케이스 (``failing_testcases.csv``)
    * 통과 테스트 케이스 (``passing_testcases.csv``)
    * 버기 라인을 실행했으나 우연히 통과하는 테스트 케이스 (``cc_testcaes.csv``)
* 각 테스트 케이스의 실제 소스 코드는 ``buggy_code_file_per_bug_version/original_version/main.cpp`` 파일에서 tc_name을 활용해서 확인할 수 있습니다.

### 8.2 테스트 케이스 소스 코드 확인 방법 (예시)
* 타깃 테스트 케이스 정보:
    * 버그 버전: ``bug100``
    * 테스트 케으스 정보 디렉토리: ``test_case_info_per_bug_version/bug100/``
    * 테스트 케이스 분류: ``failing_testcases.csv``
    * tc_id: ``TC98``
    * tc_name: ``CharReaderFailIfExtraTest/issue107``
* **소스 코드 검색 방법**:
    1. ``buggy_code_file_per_bug_version/original_version/main.cpp`` 테스트 코드 파일을 연다
    2. tc_name 정보로부터 ``CharReaderFailIfExtraTest, issue107`` 문자열을 생성하여 테스트 코드 파일에서 검색합니다. 
* 소스 코드 예시 결과:
    ```
    JSONTEST_FIXTURE_LOCAL(CharReaderFailIfExtraTest, issue107) {
        // This is interpreted as an int value followed by a colon.
        Json::CharReaderBuilder b;
        Json::Value root;
        char const doc[] = "1:2:3";
        b.settings_["failIfExtra"] = true;
        CharReaderPtr reader(b.newCharReader());
        Json::String errs;
        bool ok = reader->parse(doc, doc + std::strlen(doc), &root, &errs);
        JSONTEST_ASSERT(!ok);
        JSONTEST_ASSERT_STRING_EQUAL("* Line 1, Column 2\n"
                                    "  Extra non-whitespace after JSON value.\n",
                                    errs);
        JSONTEST_ASSERT_EQUAL(1, root.asInt());
    }
    ```


## 9. 데이터셋의 오류 탐지 정확도 평가 (총 165개 버그 버전, 총 363개 함수)
* 각 오류 탐지 공식 별 **함수 단위**로 버기 함수 탐지 정확도 결과

### 9.1 스펙트럼 기반 정확도 (SBFL)
SBFL 공식 | ``acc@5`` 버그 개수 | ``acc@5`` 정확도 백분율 | ``acc@10`` 버그 개수 | ``acc@10`` 정확도 백분율
--- | --- | --- | --- | --- |
Binary | 0 | 0.00% | 0 | 0.00%
GP13 | 1136 | 82.42% | 153 | 92.72%
Jaccard | 1136 | 82.42% | 153 | 92.72%
Naish1 | 1136 | 82.42% | 153 | 92.72%
Naish2 | 1136 | 82.42% | 153 | 92.72%
Ochiai | 1136 | 82.42% | 153 | 92.72%
Russel+Rao | 0 | 0.00% | 0 | 0.00%
Wong1 | 0 | 0.00% | 0 | 0.00%


### 9.2 변이 기반 정확도 (MBFL)
MBFL 공식 | ``acc@5`` 버그 개수 | ``acc@5`` 정확도 백분율 | ``acc@10`` 버그 개수 | ``acc@10`` 정확도 백분율
--- | --- | --- | --- | --- |
Metallaxis | 160 | 96.96% | 165 | 100.00%
MUSE | 159 | 96.36% | 165 | 100.00%

