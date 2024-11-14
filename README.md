# 결함위치탐지 데이터셋 생성 결과


## 프로젝트 데이터셋의 문서 링크
1. jsoncpp: [jsoncpp-문서](/documents/dataset_description/document-jsoncpp.md)
2. libxml2: [libxml2-문서](/documents/dataset_description/document-libxml2.md)
3. NSFW_cpp: [NSFW_cpp-문서](/documents/dataset_description/document-NSFW_cpp.md)
4. NSFW_c: [NSFW_c-문서](/documents/dataset_description/document-NSFW_c.md)
5. opencv
    * dnn: [dnn-문서](/documents/dataset_description/opencv/document-opencv_dnn.md)
    * core: [core-문서](/documents/dataset_description/opencv/document-opencv_core.md)
    * imgproc: [imgproc-문서](/documents/dataset_description/opencv/document-opencv_imgproc.md)
    * calib3d: [calib3d-문서](/documents/dataset_description/opencv/document-opencv_calib3d.md)
    * features2d: [features2d-문서](/documents/dataset_description/opencv/document-opencv_features2d.md)


## 프로젝트의 데이터셋 파일 링크
1. jsoncpp: [jsoncpp-데이터셋-링크](https://drive.google.com/file/d/1R0HTSE3MHSujkNHrmaOGyFRK-5dA4kEk/view?usp=drive_link)
2. libxml2: [libxml-데이터셋-링크](https://drive.google.com/file/d/10HP8t0W60VNx1oAAhmggFFZfZazHChf3/view?usp=drive_link)
3. NSFW_cpp: 8월에 LIGNex1에 기전달
4. NSFW_c: 8월에 LIGNex1에 기전달
5. opencv
    * dnn: [opencv_dnn-데이터셋-링크](https://drive.google.com/file/d/1mL6lSmlHK4sefuCf0Zl6uOOiftZTh8Wy/view?usp=drive_link)
    * core: [opencv_core-데이터셋-링크](https://drive.google.com/file/d/1gQua9HCkridZxemDJJ2XZfHFxuRiQ1xs/view?usp=drive_link)
    * imgproc: [opencv_imgproc-데이터셋-링크](https://drive.google.com/file/d/14W1waiEUk4oh6p9bewN_za5-vGdQMoj2/view?usp=drive_link)
    * calib3d: [opencv_calib3d-데이터셋-링크](https://drive.google.com/file/d/14xNBpvdK_GpyPe6B_C_tnmHeyl4SjtfQ/view?usp=drive_link)
    * features2d: [opencv_features2d-데이터셋-링크](https://drive.google.com/file/d/17NsIqm2wrB9gi5XW2Q9hf-iGqtJN6WHy/view?usp=drive_link)


## 결함위치탐지 학습 데이터셋 파일 개수
* SBFL 기반 feature csv 파일 데이터: 총 1,471개
    프로젝트 | 파일 개수 |
    --|--|
    jsoncpp | 165개
    libxml2 | 152개
    NSFW_cpp | 8월에 LIGNex1에 기전달
    NSFW_c | 8월에 LIGNex1에 기전달
    opencv_dnn | 182개
    opencv_core | 258개
    opencv_imgproc | 207개
    opencv_calib3d | 211개
    opencv_features2d | 296개

* MBFL 기반 변이 소스 코드 파일 데이터: 총 85,897개
    프로젝트|파일 개수|
    --|--|
    [jsoncpp](https://drive.google.com/file/d/1h9-tREd5DxgTUI_l5EvUCjqkTAtdV94a/view?usp=sharing) | 2,190개
    [libxml2](https://drive.google.com/file/d/1aCg8yPBIhACDQSuYf_st5n7hQNxBCGuz/view?usp=sharing) | 27,769개
    NSFW_cpp | 8월에 LIGNex1에 기전달
    NSFW_c | 8월에 LIGNex1에 기전달
    [opencv_dnn](https://drive.google.com/file/d/1hELKmZccOMtPQ2DA_ncfElEqSin2Zn8J/view?usp=sharing) | 12,123개
    [opencv_core](https://drive.google.com/file/d/1UmNNy_whRprx78OPU3dclQGT_wzRjSTr/view?usp=sharing) | 7,839개
    [opencv_imgproc](https://drive.google.com/file/d/1KnAgqLUanQsel1uJknUjbdyE9TfnloJk/view?usp=sharing) | 13,612개
    [opencv_calib3d](https://drive.google.com/file/d/1SQNvUzLQB3ZgYjTqdCyzJsNsqFtpTZ1_/view?usp=sharing) | 12,451개
    [opencv_features2d](https://drive.google.com/file/d/150cY2b0_0XZsS0iBfy816it2lw91SUum/view?usp=sharing) | 9,913개



## SBFL/MBFL 기반 데이터 생성 도구 설명
* [FL-Dataset-Generating-Tool](/documents/README-kor.md)


## 결함위치탐지 데이터셋에 대한 평가 결과
1. jsoncpp: [jsoncpp-평가결과](/documents/dataset_description/document-jsoncpp.md#9-데이터셋의-오류-탐지-정확도-평가-총-165개-버그-버전-총-363개-함수)
2. libxml2: [libxml2-평가결과](/documents/dataset_description/document-libxml2.md#9-데이터셋의-결함-위치-탐지-정확도-평가-총-152개-버그-버전-총-918개-함수)
3. NSFW_cpp: [NSFW_cpp-평가결과](/documents/dataset_description/document-NSFW_cpp.md#9-데이터셋의-결함-위치-탐지-정확도-평가-총-378개-버그-버전)
4. NSFW_c: [NSFW_c-평가결과](/documents/dataset_description/document-NSFW_c.md#9-데이터셋의-결함-위치-탐지-정확도-평가-총-709개-버그-버전)
5. opencv
    * dnn: [dnn-평가결과](/documents/dataset_description/opencv/document-opencv_dnn.md#9-데이터셋의-결함-위치-탐지-정확도-평가-총-182개-버그-버전)
    * core: [core-평가결과](/documents/dataset_description/opencv/document-opencv_core.md#9-데이터셋의-결함-위치-탐지-정확도-평가-총-258개-버그-버전)
    * imgproc: [imgproc-평가결과](/documents/dataset_description/opencv/document-opencv_imgproc.md#9-데이터셋의-결함-위치-탐지-정확도-평가-총-207개-버그-버전)
    * calib3d: [calib3d-평가결과](/documents/dataset_description/opencv/document-opencv_calib3d.md#9-데이터셋의-결함-위치-탐지-정확도-평가-총-211개-버그-버전)
    * features2d: [features2d-평가결과](/documents/dataset_description/opencv/document-opencv_features2d.md#9-데이터셋의-결함-위치-탐지-정확도-평가-총-296개-버그-버전)

---
마지막 업데이트 2024년 11월 14일
