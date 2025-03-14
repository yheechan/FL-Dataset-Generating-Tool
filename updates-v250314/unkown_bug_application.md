# FL 데이터셋 생성 도구를, 결함위치를 알고있지 않는 오픈소스에 적용 예제

# zlib_ng 결함 구성
```
real_world_buggy_versions/
└── inflate.unknownIssue.c
    ├── buggy_code_file
    │   └── inflate.unknownIssue.c
    ├── bug_info.csv
    └── testsuite_info
        ├── failing_tcs.txt
        └── passing_tcs.txt
```
* 해당 결함, ``inflate.unkownIssue.c``는 ``inflate.c`` 소스 코드 파일에 ``78``번째 줄을 ``state->hold = 100;``로 수정하여 만든 버그 버전이다.
* 총 ``14개의`` 실패 테스트 케이스와 ``754개의`` 패싱 테스트 케이스가 있다.
* ``bug_info.csv`` 파일에는 다음과 같이 내용을 정리한다. 이때, 결함위치를 알고있지 않기때문에 ``buggy_lineno``는 ``-1``을 준다.
    ```
    target_code_file,buggy_code_file,buggy_lineno
    zlib_ng/inflate.c,inflate.unknownIssue.c,-1
    ```
* 결함에 대한 정보를 위와 같이 구성이 완료된 후 결함위치탐지 데이터셋 추출 명령어 순서는 다음과 같다.
    ```
    $ time python3 select_usable_versions.py --subject zlib_ng
    $ time python3 prepare_prerequisites.py --subject zlib_ng --target-set-name usable_buggy_versions
    $ time python3 extract_mbfl_features.py --subject zlib_ng --target-set-name prerequisite_data --trial trial1 --dont-terminate-leftovers
    time python3 extract_sbfl_features.py --subject zlib_ng --target-set-name mbfl_features
    ```
