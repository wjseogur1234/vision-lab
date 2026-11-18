---
type: overview
tags: []
sources: []
created: 2026-11-16
updated: 2026-11-16
---

# Overview — vision-lab

> [!note] `raw/`에 ingest된 소스는 아직 없다. 데이터셋 페이지는 원본 폴더를 직접 읽어서 썼다.

## 프로젝트 목표
LibreYOLO로 vision AI 모델을 학습한다. 첫 과제는 AI Hub 101 데이터를 이용한 CCTV 보행자 검출이다.

## 진행 단계
- 준비: 프로젝트 구성, 라이브러리 환경
- Phase 0: 데이터셋 구조, 데이터셋 불러오기 구조
- Phase 1: 학습
- Phase 2: 추론, API 설계 (모델이 보여주는 추론 값, 모델 호출)
- Phase 3: 테스트, 평가 (checkpoint에 따른 성능 결과)
- Phase 4: vision task 확장

현재는 준비 단계를 마치고 Phase 0을 시작하는 시점이다.

## 현재 이해
- 원본 데이터셋은 3개다: [[aihub-101-cctv]], [[aihub-095-accident]], [[aihub-110-child-zone]].
- 첫 과제에는 [[aihub-101-cctv]]의 Bbox만 쓴다. 이미지 163,913장, 장소 37곳, 카메라 70대다(라벨 기준, Training과 Validation의 합).
- 원본은 zip이다. 필요한 이미지만 꺼내서 YOLO 형식으로 바꾼다. (출처: [[dataset-split-plan]])
- AI Hub의 공식 구분은 카메라가 겹친다. 장소 단위로 다시 나누는 것을 제안한다. (출처: [[dataset-split-plan]])

## 열린 질문
- 분할 방법, 클래스 구성, 저장 경로를 정해야 한다. ([[dataset-split-plan]] 7절)
- 101 라벨의 `guideline`이 무엇인지 확인해야 한다. ([[aihub-101-cctv]] 3.3절)
- 101 Tracking의 Validation 원천 zip 1개가 열리지 않는다. 다시 받아야 하는지 확인해야 한다. ([[aihub-101-cctv]] 4절)
