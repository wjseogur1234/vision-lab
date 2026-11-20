---
type: overview
tags: []
sources: []
created: 2026-11-16
updated: 2026-11-20
---

# Overview — vision-lab

> [!note] 데이터셋 구성은 2026-11-20에 확인했다.

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
- `data/raw/`에 데이터셋별 링크가 있다.
- 링크 대상은 `/mnt/data1/downloads/dataset_hdd-8tb/interim/`이다.
- 전처리는 풀려 있는 이미지와 라벨을 읽는다. ([[dataset-split-plan]])
- AI Hub의 공식 구분은 카메라가 겹친다. 장소 단위로 다시 나누는 것을 제안한다. (출처: [[dataset-split-plan]])

## 열린 질문
- 분할 방법, 클래스 구성, 저장 경로를 정해야 한다. ([[dataset-split-plan]] 7절)
- 101 라벨의 `guideline`이 무엇인지 확인해야 한다. ([[aihub-101-cctv]] 3.3절)
- 101의 라벨과 실제 이미지 대응을 확인해야 한다. ([[aihub-101-cctv]] 2.1절)
