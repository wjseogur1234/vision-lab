# Index

위키 전체 카탈로그. 규칙은 `docs/AGENTS.md`의 "목차 구성 지침".
대분류는 **Phase** 기준(공통 / Phase 0~4)이며, 폴더(`phase_N/`)와 같다. Phase 폴더 안의 하위 폴더(`entities/` 등)는 페이지 **종류**를 나타낸다.

## 공통 — 목표, 진행 단계, 요구사항
### 종합
- [overview](overview.md) — 프로젝트 목표·진행 단계·열린 질문

## Phase 0 — 데이터셋 구조, 전처리, 불러오기
### 원본 데이터셋
- [aihub-101-cctv](phase_0/entities/aihub-101-cctv.md) — AI Hub 101 CCTV 교통 데이터. Bbox·Tracking·Segmantation 구조, 라벨 JSON 형식, 수치 (주 데이터셋. Tracking·Segmantation은 Phase 4 후보)
- [aihub-095-accident](phase_0/entities/aihub-095-accident.md) — AI Hub 095 교통사고 영상. mp4와 영상 단위 JSON, 상자 라벨 없음 (Phase 2 추론 확인 영상 후보)
- [aihub-110-child-zone](phase_0/entities/aihub-110-child-zone.md) — AI Hub 110 어린이 보호구역 위험행동. 4K 프레임, VOC XML, 현재 파일 수

### 전처리
- [raw-manifest](phase_0/analyses/raw-manifest.md) — 원본 CSV 열, 파일 대응 결과, 누락 확인 방법
- [dataset-split-plan](phase_0/analyses/dataset-split-plan.md) — 분할 계획. 장소 단위 분할, 장소별 수, COCO JSON 결과 구조, mini 검증 결과 (일부 미정)
- [libreyolo-dataset-formats](phase_0/concepts/libreyolo-dataset-formats.md) — 작업별 라벨, YAML, 파일 구조

### 결정
- [adr-0001-coco-json-labels](../adr/adr-0001-coco-json-labels.md) — 라벨 형식 COCO JSON, 이미지 복사 없음 (승인)
- [adr-0002-scripts-by-output-stage](../adr/adr-0002-scripts-by-output-stage.md) — 실행 스크립트 산출물 단계 분리, Hydra는 scripts만 (승인)

## Phase 1 — 학습
### 설계
- [training-architecture](phase_1/analyses/training-architecture.md) — 학습 구조 설계안. 요구사항, 모듈, 호출 관계, 설정, LibreYOLO 연동 지점 (제안)

### 객체 검출
- [libreyolo-models](phase_1/analyses/libreyolo-models.md) — 보행자 검출 후보, 설치 조건, 실행 환경, 검증 범위

### 실험 관리
- [libreyolo-mlflow](phase_1/analyses/libreyolo-mlflow.md) — MLflow 지원 여부, MLflowLogger 사용법, 기록 항목, 도입 할 일 (규격 미정)

### 원자료
- [libreyolo-model-reference](phase_1/sources/libreyolo-model-reference.md) — LibreYOLO 모델 목록과 PyPI 배포 정보

## Phase 2 — 추론, API
(페이지 없음)

## Phase 3 — 테스트, 평가
(페이지 없음)

## Phase 4 — vision task 확장
(페이지 없음)
