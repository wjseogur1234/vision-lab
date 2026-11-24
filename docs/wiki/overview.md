---
type: overview
tags: []
sources: []
created: 2026-11-16
updated: 2026-11-24
---

# Overview — vision-lab

> [!note] 진행 상태는 2026-11-24 기준이다.

## 프로젝트 목표
LibreYOLO로 vision AI 모델을 학습한다. 첫 과제는 CCTV 보행자 검출이다.

## 진행 단계
- 준비: 프로젝트 구성, 라이브러리 환경
- Phase 0: 데이터셋 구조, 데이터셋 불러오기 구조
- Phase 1: 학습
- Phase 2: 추론, API 설계 (모델이 보여주는 추론 값, 모델 호출)
- Phase 3: 테스트, 평가 (checkpoint에 따른 성능 결과)
- Phase 4: vision task 확장

현재는 Phase 0을 진행하고 있다.
mini 데이터셋으로 COCO 생성과 학습 1 epoch를 확인했다.
다음은 분할 안 고정과 전체 v1 생성이다.

## 현재 이해
- 원본 데이터셋은 3개다: [aihub-101-cctv](entities/aihub-101-cctv.md), [aihub-095-accident](entities/aihub-095-accident.md), [aihub-110-child-zone](entities/aihub-110-child-zone.md).
- 첫 과제에는 [aihub-101-cctv](entities/aihub-101-cctv.md) Bbox와 [aihub-110-child-zone](entities/aihub-110-child-zone.md)을 쓴다.
- 101 Bbox의 라벨은 이미지 163,913장을 포함한다.
- 110의 사용 절차는 [dataset-split-plan 6절](analyses/dataset-split-plan.md#6-ai-hub-110-사용-계획)에 있다.
- `data/raw/`에 데이터셋별 링크가 있다.
- 링크 대상은 `/mnt/data1/downloads/dataset_hdd-8tb/interim/`이다.
- 전처리는 풀려 있는 이미지와 라벨을 읽는다. ([dataset-split-plan](analyses/dataset-split-plan.md))
- AI Hub의 공식 구분은 카메라가 겹친다. 장소 단위로 다시 나누기로 했다. (출처: [dataset-split-plan](analyses/dataset-split-plan.md))
- 클래스는 `person` 1개다. 라벨은 COCO JSON이다. 이미지는 복사하지 않고 원본 경로를 쓴다.
- 101 Bbox의 JPG 163,901장이 라벨과 1대1로 연결됐다. ([raw-manifest](analyses/raw-manifest.md))

## 열린 질문
- 장소 배정 안, 배경 비율, 카메라별 프레임 상한을 정해야 한다. ([dataset-split-plan 7절](analyses/dataset-split-plan.md#7-정해야-할-것))
- 전체 v1을 HDD에서 읽을 때 학습 속도를 확인해야 한다.
- 101 라벨의 `guideline`이 무엇인지 확인해야 한다. ([aihub-101-cctv 3.3절](entities/aihub-101-cctv.md#33-라벨-json-형식))
