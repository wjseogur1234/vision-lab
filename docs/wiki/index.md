# Index

위키 전체 카탈로그. 규칙은 `docs/AGENTS.md`의 "목차 구성 지침".
대분류는 **주제** 기준(기획 / 데이터 / 모델 / 자료)이며, 폴더(`requirements/`, `entities/` 등)는 페이지 **종류**를 나타낸다.

## 기획 — 목표, 요구사항, 탐지 대상
### 종합
- [overview](overview.md) — 프로젝트 목표·진행 단계·열린 질문

## 데이터 — 데이터셋 구조, 전처리, 불러오기
### 원본 데이터셋
- [aihub-101-cctv](entities/aihub-101-cctv.md) — AI Hub 101 CCTV 교통 데이터. Bbox·Tracking·Segmantation 구조, 라벨 JSON 형식, 수치 (주 데이터셋)
- [aihub-095-accident](entities/aihub-095-accident.md) — AI Hub 095 교통사고 영상. mp4와 영상 단위 JSON, 상자 라벨 없음
- [aihub-110-child-zone](entities/aihub-110-child-zone.md) — AI Hub 110 어린이 보호구역 위험행동. 4K 프레임, VOC XML, 현재 파일 수

### 전처리
- [raw-manifest](analyses/raw-manifest.md) — 원본 CSV 열, 파일 대응 결과, 누락 확인 방법
- [dataset-split-plan](analyses/dataset-split-plan.md) — 분할 계획. 장소 단위 분할, COCO JSON 결과 구조, mini 검증 결과 (일부 미정)
- [libreyolo-dataset-formats](concepts/libreyolo-dataset-formats.md) — 작업별 라벨, YAML, 파일 구조

## 모델 — 학습, 추론·API, 평가
### 객체 검출
- [libreyolo-models](analyses/libreyolo-models.md) — 보행자 검출 후보, 설치 조건, 실행 환경, 검증 범위

## 자료 — 원자료 요약 (sources)
### 공식 문서
- [libreyolo-model-reference](sources/libreyolo-model-reference.md) — LibreYOLO 모델 목록과 PyPI 배포 정보
