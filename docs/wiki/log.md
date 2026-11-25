# Log

최신 기록부터 표시한다. 규칙은 `docs/AGENTS.md`의 "index.md / log.md".

## [2026-11-26] schema | Phase 0 실행 스크립트 분리
- 근거: `src/data/`의 실행 로직을 `scripts/`로 옮겼다. 같은 이름의 데이터셋은 버전을 올린다.
- 갱신: [dataset-split-plan](phase_0/analyses/dataset-split-plan.md), [raw-manifest](phase_0/analyses/raw-manifest.md)

## [2026-11-24] schema | Phase 폴더로 위키 재구성
- 규칙: 최상위 폴더를 `phase_0`~`phase_4`로 나눈다. 종류 폴더는 Phase 폴더 안에 둔다.
- 규칙: `index.md` 대분류를 `공통`, `Phase 0`~`Phase 4`로 바꾼다.
- 이동: Phase 0에 데이터셋 3개, raw-manifest, dataset-split-plan, libreyolo-dataset-formats.
- 이동: Phase 1에 libreyolo-models, libreyolo-mlflow, libreyolo-model-reference.
- 수정: 모든 상대 링크와 frontmatter `sources` 경로.
- 갱신: `docs/AGENTS.md`, [index](index.md)

## [2026-11-24] query | 장소별 배정 목록과 수
- 근거: `configs/data/aihub101-ped-v1.splits.yaml`, `data/interim/raw-manifests/101/manifest.csv`.
- 추가: 장소별 카메라 수, 이미지 수, 배정 안에서 확인한 점.
- 갱신: [dataset-split-plan](phase_0/analyses/dataset-split-plan.md), [index](index.md)

## [2026-11-24] lint | 문서 전체 일치 점검
- 수정: README 폴더 구조에 `docs/`, `outputs/`를 넣고 `weights/` 위치를 바로잡았다.
- 추가: AGENTS.md와 분할 계획 7절에 학습 결과 경로 `outputs/`.
- 갱신: [dataset-split-plan](phase_0/analyses/dataset-split-plan.md)

## [2026-11-24] lint | 진행 상황 갱신
- 수정: 학습 결과 경로 `data/interim/runs` → `outputs/runs`.
- 갱신: [overview](overview.md), [dataset-split-plan](phase_0/analyses/dataset-split-plan.md)

## [2026-11-24] query | LibreYOLO MLflow 지원 여부
- 근거: 설치된 `libreyolo==1.8.0` 코드, [Experiment loggers](https://www.libreyolo.com/docs/train/loggers).
- 생성: [libreyolo-mlflow](phase_1/analyses/libreyolo-mlflow.md)
- 갱신: [libreyolo-model-reference](phase_1/sources/libreyolo-model-reference.md), [libreyolo-models](phase_1/analyses/libreyolo-models.md), [index](index.md)

## [2026-11-24] lint | 공식 문서 대조와 미확인 주장 점검
- 근거: [형식 문서](https://www.libreyolo.com/docs/reference/dataset-formats), [학습 데이터셋 문서](https://www.libreyolo.com/docs/train/datasets), `data/raw/`의 101 JSON과 110 파일.
- 갱신: [libreyolo-dataset-formats](phase_0/concepts/libreyolo-dataset-formats.md), [aihub-101-cctv](phase_0/entities/aihub-101-cctv.md), [aihub-110-child-zone](phase_0/entities/aihub-110-child-zone.md)

## [2026-11-24] lint | 결정 사항과 mini 검증 결과 반영
- 근거: `configs/data/aihub101-ped-v1.splits.yaml`, `data/processed/aihub101-ped-mini/metadata.yaml`, `data/interim/runs/smoke-mini/`.
- 결정: 장소 단위 분할, 클래스 `person` 1개, 결과 경로 `data/processed/`.
- 수정: 해결된 미정 항목, 낡은 "학습 실행 안 함" 표현, `raw-manifest` frontmatter의 `sources` 형식.
- 갱신: [dataset-split-plan](phase_0/analyses/dataset-split-plan.md), [libreyolo-models](phase_1/analyses/libreyolo-models.md), [libreyolo-dataset-formats](phase_0/concepts/libreyolo-dataset-formats.md), [raw-manifest](phase_0/analyses/raw-manifest.md), [aihub-101-cctv](phase_0/entities/aihub-101-cctv.md), [aihub-110-child-zone](phase_0/entities/aihub-110-child-zone.md), [overview](overview.md), [index](index.md)

## [2026-11-24] lint | 이미지 복사 없이 원본 경로 사용
- 근거: LibreYOLO는 YAML 루트와 COCO `file_name`을 이어서 이미지를 읽는다.
- 갱신: [dataset-split-plan](phase_0/analyses/dataset-split-plan.md)

## [2026-11-24] query | 원본 manifest 생성 결과
- 근거: `data/interim/raw-manifests/`의 CSV 3개를 집계했다.
- 생성: [raw-manifest](phase_0/analyses/raw-manifest.md)
- 갱신: [index](index.md), [dataset-split-plan](phase_0/analyses/dataset-split-plan.md)

## [2026-11-21] lint | manifest 이미지 경로 예시 수정
- 갱신: [dataset-split-plan](phase_0/analyses/dataset-split-plan.md)

## [2026-11-21] lint | 데이터셋 계획과 실행 환경 정리
- 갱신: [dataset-split-plan](phase_0/analyses/dataset-split-plan.md), [libreyolo-models](phase_1/analyses/libreyolo-models.md)

## [2026-11-21] query | manifest.csv 구성 확정
- 결정: COCO JSON과 별도 CSV로 둔다.
- 갱신: [dataset-split-plan](phase_0/analyses/dataset-split-plan.md)

## [2026-11-21] query | 라벨 형식을 COCO JSON으로 변경
- 갱신: [dataset-split-plan](phase_0/analyses/dataset-split-plan.md), [aihub-101-cctv](phase_0/entities/aihub-101-cctv.md), [index](index.md)

## [2026-11-21] query | LibreYOLO 데이터셋 규격
- 근거: 사용자가 제공한 데이터셋 형식 문서.
- 생성: [libreyolo-dataset-formats](phase_0/concepts/libreyolo-dataset-formats.md)
- 갱신: [index](index.md), [dataset-split-plan](phase_0/analyses/dataset-split-plan.md), [libreyolo-models](phase_1/analyses/libreyolo-models.md), [libreyolo-model-reference](phase_1/sources/libreyolo-model-reference.md)

## [2026-11-21] query | LibreYOLO 모델별 검출 데이터 형식
- 갱신: [libreyolo-models](phase_1/analyses/libreyolo-models.md), [libreyolo-model-reference](phase_1/sources/libreyolo-model-reference.md)

## [2026-11-20] schema | 상대 경로 Markdown 링크
- 갱신: [위키 규칙](../AGENTS.md)

## [2026-11-20] query | AI Hub 110 사용 계획
- 갱신: [overview](overview.md), [aihub-110-child-zone](phase_0/entities/aihub-110-child-zone.md), [dataset-split-plan](phase_0/analyses/dataset-split-plan.md)

## [2026-11-20] query | data/raw 데이터셋 구성
- 근거: `data/raw/`의 링크, 폴더, 파일 수를 확인했다.
- 갱신: [aihub-095-accident](phase_0/entities/aihub-095-accident.md), [aihub-101-cctv](phase_0/entities/aihub-101-cctv.md), [aihub-110-child-zone](phase_0/entities/aihub-110-child-zone.md), [dataset-split-plan](phase_0/analyses/dataset-split-plan.md), [overview](overview.md), [index](index.md)

## [2026-11-19] query | LibreYOLO 보행자 검출 모델
- 생성: [libreyolo-models](phase_1/analyses/libreyolo-models.md), [libreyolo-model-reference](phase_1/sources/libreyolo-model-reference.md)
- 갱신: [index](index.md)

## [2026-11-16] query | 원본 데이터셋 구조와 분할 방법
- 근거: `/mnt/data1/downloads/교통데이터`의 원본 폴더와 zip을 직접 읽었다. `raw/`에 ingest한 문서는 없다.
- 생성: [aihub-101-cctv](phase_0/entities/aihub-101-cctv.md), [aihub-095-accident](phase_0/entities/aihub-095-accident.md), [aihub-110-child-zone](phase_0/entities/aihub-110-child-zone.md), [dataset-split-plan](phase_0/analyses/dataset-split-plan.md)
- 갱신: [index](index.md), [overview](overview.md)

## [2026-11-16] schema | LLM Wiki 구조 생성
- 생성: `docs/AGENTS.md`, [index](index.md), [overview](overview.md), `raw/`, `wiki/` 하위 폴더
