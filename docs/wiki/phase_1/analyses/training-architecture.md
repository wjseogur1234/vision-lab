---
type: analysis
tags: [architecture, training, libreyolo, hydra, mlflow]
sources: ["wiki/phase_1/analyses/libreyolo-models.md", "wiki/phase_1/analyses/libreyolo-mlflow.md", "adr/adr-0002-scripts-by-output-stage.md"]
created: 2026-11-26
updated: 2026-11-27
---

# Phase 1 학습 구조 설계

> [!note] 상태: 제안 (2026-11-26)
> 구현 전 설계안이다. 사용자 검토 후 확정한다.
> 확정되면 되돌리기 어려운 결정은 ADR로 남긴다.

## 1. 요구사항

### 1.1 기능 요구사항

| ID | 요구사항 |
|---|---|
| F1 | `build_coco`가 만든 데이터셋으로 검출 모델을 학습한다 |
| F2 | 모델, 데이터셋, 학습 값을 설정 파일로 고른다 |
| F3 | 명령줄에서 설정 값을 덮어쓴다 |
| F4 | 학습 지표와 설정을 MLflow에 기록한다 |
| F5 | 데이터 출처와 코드 출처를 run에 붙인다 |
| F6 | 중단된 학습을 이어서 한다 |
| F7 | mini 데이터셋으로 빠른 확인 학습(smoke)을 한다 |

### 1.2 비기능 요구사항

| ID | 요구사항 |
|---|---|
| N1 | 모든 실행은 Docker `lab`에서 한다 |
| N2 | LibreYOLO 패키지 코드는 고치지 않는다 |
| N3 | Hydra와 OmegaConf는 `scripts/`에서만 쓴다 ([ADR-0002](../../../adr/adr-0002-scripts-by-output-stage.md)) |
| N4 | 같은 설정과 seed면 같은 데이터 순서로 학습한다 |
| N5 | 학습 결과 이름이 겹치면 덮어쓰지 않는다 |
| N6 | `data/raw/<데이터셋>`은 심볼릭 링크로 둔다. 직접 마운트하면 시작 전 탐색이 3분 이상 걸린다 ([LibreYOLO #1078](https://github.com/LibreYOLO/libreyolo/issues/1078)) |
| N7 | 데이터 로더 worker는 `forkserver`로 띄운다. MLflow run이 열린 채 fork하면 학습이 멈춘다 (10.1절) |
| N8 | run에 git 커밋과 수정 여부를 남긴다. 컨테이너에 git을 설치했다(2026-11-26) |

### 1.3 범위 밖

- 테스트 분할 평가와 checkpoint 비교: Phase 3.
- 추론과 API: Phase 2.
- 검출 외 작업: Phase 4.

## 2. 핵심 기능

1. 학습 실행: 설정을 읽고 LibreYOLO `train()`을 부른다.
2. 사전 점검: 데이터셋 YAML, COCO JSON, `data/raw/` 링크를 확인한다.
3. 출처 수집: 데이터셋 `metadata.yaml`, 분할 파일 해시, git 커밋을 모은다.
4. 실험 기록: `MLflowLogger`를 만들고 출처를 tag로 붙인다.
5. 결과 요약: 최종 지표와 가중치 경로를 로그에 남긴다.

## 3. 시스템 구성 요소

| 구성 요소 | 위치 | 역할 |
|---|---|---|
| 전처리 | `scripts/` 3개, `src/data/` | Phase 0. COCO 데이터셋과 YAML을 만든다 |
| 학습 스크립트 | `scripts/train.py` | Hydra 진입점. 설정을 값으로 풀어 라이브러리에 넘긴다 |
| 학습 라이브러리 | `src/training/` | 점검, 출처, 기록, 실행. Hydra를 모른다 |
| 학습 설정 | `configs/train/` | 모델, 학습 값, 기록 설정 |
| 데이터셋 설정 | `configs/data/<이름>.yaml` | `build_coco`가 만든다. 학습이 읽는다 |
| LibreYOLO | 패키지 `libreyolo==1.8.0` | 모델, 데이터 로딩, 학습 루프 |
| MLflow 클라이언트 | 패키지 `mlflow` (`libreyolo[mlflow]`) | 학습 중 서버로 기록한다 |
| MLflow 서버 | `compose.yaml`의 `mlflow` 서비스 | 기록 저장, 웹 화면. DB는 SQLite 1개 |
| 결과 | `outputs/runs/<run>/` | 가중치, `metrics.jsonl`, `train_config.yaml` |
| 기록 저장소 | `outputs/mlflow/` | `mlflow.db`, artifact 폴더 |

## 4. 디렉터리 구조

`+`는 새로 만든다.

```
configs/
├── data/                  # build_coco 산출물 (기존)
├── prep/                  # 전처리 설정 (기존)
└── train/                 # +
    ├── train.yaml         # + 기본 설정. defaults 목록
    ├── model/             # + yolox-s.yaml, yolo9-t.yaml ...
    ├── tracking/          # + mlflow.yaml, none.yaml
    └── experiment/        # + smoke.yaml, baseline.yaml
scripts/
├── _common.py             # 기존. setup_logging, to_args
└── train.py               # +
src/
├── data/                  # 기존
└── training/              # +
    ├── __init__.py
    ├── checks.py          # 사전 점검
    ├── provenance.py      # 데이터·코드 출처
    ├── tracking.py        # MLflowLogger 상속 클래스
    └── runner.py          # LibreYOLO 호출
outputs/
├── runs/                  # 학습 결과
└── mlflow/                # + mlflow.db, artifacts/
compose.yaml               # + mlflow 서비스
```

- `pyproject.toml`의 wheel 대상에 `src/training`을 추가한다.
- `train` 그룹을 `libreyolo[mlflow]==1.8.0`으로 바꾼다.

## 5. 모듈별 책임

| 모듈 | 책임 | 하지 않는 것 |
|---|---|---|
| `scripts/train.py` | Hydra 설정 읽기, 값 풀기, worker 시작 방식 지정, 함수 순서대로 호출, 종료 코드 | 계산, 파일 쓰기 |
| `training.checks` | 데이터셋 YAML과 COCO JSON 존재 확인. `data/raw/` 항목이 링크인지 확인 | 이미지 열기 |
| `training.provenance` | `metadata.yaml` 읽기, 분할 파일 해시, `git` 명령으로 커밋과 수정 여부 | MLflow 호출 |
| `training.tracking` | `MLflowLogger` 상속. run을 연 직후 tag를 붙이고, 끝날 때 `metrics.jsonl`과 `best.pt`를 올린다 | 학습 실행 |
| `training.runner` | 가중치 경로로 모델 생성, `train()` 호출, 결과 dict 반환. run 이름 충돌 처리 | 설정 해석 |

## 6. 모듈 간 의존성

```mermaid
flowchart LR
    S[scripts/train.py] --> C[scripts/_common]
    S --> CK[training.checks]
    S --> P[training.provenance]
    S --> T[training.tracking]
    S --> R[training.runner]
    C --> H[(hydra / omegaconf)]
    S --> H
    T --> M[(mlflow)]
    T --> L[(libreyolo)]
    R --> L
    CK --> Y[(pyyaml)]
    P --> Y
```

- `src/training/`은 `src/data/`를 import하지 않는다. 둘은 파일(YAML, `metadata.yaml`)로만 연결된다.
- `src/training/` 모듈끼리는 서로 import하지 않는다. 스크립트가 반환값을 다음 함수로 넘긴다.
- `libreyolo`는 `tracking`과 `runner`만 import한다.

## 7. 함수 호출 관계

```mermaid
sequenceDiagram
    participant U as 사용자
    participant S as scripts/train.py
    participant CK as checks
    participant P as provenance
    participant T as tracking
    participant R as runner
    participant L as LibreYOLO
    U->>S: python scripts/train.py data=... model=...
    S->>S: to_args(cfg)
    S->>S: set_start_method("forkserver")
    S->>CK: check_dataset(data_yaml, raw_dir)
    CK-->>S: dataset_dir
    S->>P: collect(dataset_dir, repo_dir)
    P-->>S: tags (dict)
    S->>R: free_run_name(project, name)
    R-->>S: name
    S->>T: make_loggers(tracking, experiment, name, tags)
    T-->>S: loggers
    S->>R: train(weights, data_yaml, options, loggers)
    R->>L: LibreYOLO(weights).train(data, ..., loggers)
    L-->>T: on_train_start → start_run, log_params, set_tags
    L-->>T: on_train_epoch_end → log_metrics
    L-->>T: on_train_end → log_artifact, end_run
    L-->>R: result dict
    R-->>S: result
    S->>U: 지표, 가중치 경로 로그
```

함수 시그니처 안:

```python
# training/checks.py
def check_dataset(data_yaml: Path, raw_dir: Path) -> Path

# training/provenance.py
def collect(dataset_dir: Path, repo_dir: Path) -> dict[str, str]

# training/tracking.py
class TaggedMLflowLogger(MLflowLogger): ...
def make_loggers(kind: str, experiment: str, run_name: str,
                 tags: dict[str, str], options: dict) -> list

# training/runner.py
def free_run_name(project: Path, name: str) -> str
def train(weights: Path, data_yaml: Path, options: dict, loggers: list) -> dict
```

tag는 callback으로 붙이지 않는다. 이유는 10.1절의 2번이다.

## 8. 데이터 흐름

```mermaid
flowchart TB
    RAW[(RAW_DATA_DIR<br/>읽기 전용)] -.링크.-> DR[data/raw/&lt;데이터셋&gt;]
    subgraph Phase0[Phase 0]
      DP[data/processed/&lt;이름&gt;/<br/>annotations/*.json<br/>metadata.yaml]
      DY[configs/data/&lt;이름&gt;.yaml]
    end
    DR --> L[LibreYOLO COCODataset]
    DY --> L
    DP --> L
    DP --> PV[provenance]
    SP[configs/data/*.splits.yaml] --> PV
    GIT[(git HEAD)] --> PV
    CFG[configs/train/*] --> S[scripts/train.py]
    S --> L
    PV --> MT[MLflow tags]
    L --> OUT[outputs/runs/&lt;run&gt;/<br/>weights, results.csv]
    L --> ML[(MLflow<br/>params, metrics, artifacts)]
    MT --> ML
```

- 이미지는 `data/raw/` 링크를 따라 원본에서 읽는다. 복사하지 않는다 ([ADR-0001](../../../adr/adr-0001-coco-json-labels.md)).
- 라벨은 `data/processed/<이름>/annotations/<분할>.json`에서 읽는다.
- 학습은 `data/processed/`와 `configs/data/`를 읽기만 한다.

## 9. Configuration 관리 구조

`configs/train/train.yaml` 안:

```yaml
defaults:
  - /prep/common@_here_        # 로그 설정, Hydra 출력 끄기 재사용
  - model: yolox-s
  - tracking: mlflow
  - _self_
  - optional experiment: null

data: aihub101-ped-mini        # configs/data/<data>.yaml
name: ${model.id}_${data}      # run 이름. 겹치면 -v2, -v3
workers_start: forkserver      # 10.1절 1번
project: outputs/runs
seed: 0
train:                         # LibreYOLO train()에 그대로 넘긴다
  epochs: 100
  batch: 16
  imgsz: 640
  workers: 4
  amp: true
  patience: 50
```

`model/yolox-s.yaml`과 `tracking/mlflow.yaml` 안:

```yaml
# model/yolox-s.yaml
id: yolox-s
weights: weights/LibreYOLOXs.pt   # Python API는 모델 ID를 받지 않는다
```

```yaml
# tracking/mlflow.yaml
kind: mlflow
uri: http://mlflow:5000           # compose 서비스 이름
experiment: aihub101-ped
log_checkpoints: true
```

- 설정 그룹은 `model`, `tracking`, `experiment` 3개다.
- `tracking/none.yaml`은 MLflow 없이 학습한다. 서버가 꺼져 있을 때 쓴다.
- `train:` 아래 키는 LibreYOLO `train()` 키워드와 같은 이름을 쓴다. 스크립트가 해석하지 않고 넘긴다.
- `experiment/smoke.yaml`은 `data`, `train.epochs`만 덮어쓴다.
- 최종 설정은 `--cfg job`으로 본다. MLflow params에도 남는다.
- `--cache`는 설정에 두지 않는다. `false`로 고정한다(원본이 읽기 전용).

> [!question] `configs/prep/common.yaml` 공유
> 전처리와 학습이 같은 공통 설정을 쓸지 정해야 한다.
> 나누면 `configs/common.yaml`로 옮긴다.

## 10. LibreYOLO 연동 지점

| 지점 | LibreYOLO API | 우리 쪽 | 비고 |
|---|---|---|---|
| 모델 생성 | `LibreYOLO(model_path)` | `runner.train` | 가중치 파일 경로를 넘긴다. `"yolox-s"`는 오류 |
| 학습 | `model.train(data, *, epochs, batch, imgsz, seed, project, name, resume, callbacks, loggers, **kwargs)` | `runner.train` | `exist_ok=False` 유지 |
| 데이터 로딩 | `load_data_config`, `COCODataset` | 데이터셋 YAML | `annotations` 키가 있으면 COCO를 쓴다 |
| 실험 기록 | `libreyolo.training.MLflowLogger` | `tracking.TaggedMLflowLogger` | 상속해서 `_handle_start`, `_handle_end`를 확장한다. CLI에는 logger 옵션이 없다 |
| callback | `on_train_start`, `on_train_epoch_end`, `on_train_end`, `on_train_exception` | 쓰지 않음 | 앞의 세 hook 예외는 학습을 끝낸다. logger 예외는 그 logger만 끈다 |
| 이어하기 | `train(resume=True)` | `scripts/train.py resume=true` | 같은 run 이름을 쓴다 |
| 검증 | `model.val(data, split=...)` | Phase 3 | Phase 1은 학습 중 val만 쓴다 |

> [!warning] 알려진 제약
> `load_data_config`는 COCO를 써도 분할 이미지 폴더를 탐색한다.
> `data/raw/` 항목이 링크면 탐색 결과가 0장이고 빠르다.
> 이 동작에 기대므로 `checks`가 링크인지 확인한다. ([#1078](https://github.com/LibreYOLO/libreyolo/issues/1078))

### 10.1 MLflow 시험 결과 (2026-11-26)

조건: mini 데이터셋, yolox-s, 1 epoch, mlflow 3.18.0, 로컬 SQLite.
시험 코드는 `data/interim/mlflow-test/train_mlflow.py`다. 이 폴더는 지워질 수 있다.

기록된 것: params 84개, epoch마다 metrics 37개, tag 4개.

| # | 문제 | 원인 | 해결 |
|---|---|---|---|
| 1 | `workers=4`면 학습이 멈춘다. 오류 없이 멈춘다. 2번 재현했다 | MLflow run이 열린 상태에서 worker를 fork한다. 자식 프로세스가 잠긴 lock을 물려받는다 | `torch.multiprocessing.set_start_method("forkserver")`. `workers=4`로 정상 종료했다 |
| 2 | callback으로 tag를 붙이면 MLflow 기록이 꺼진다. 학습은 계속된다 | callback이 logger보다 먼저 실행된다. `set_tags`가 run을 먼저 연다. logger의 `start_run`이 실패한다 | `MLflowLogger`를 상속한다. `super()._handle_start()` 뒤에 `set_tags`를 부른다 |
| 3 | artifact가 `train_config.yaml` 1개만 올라간다 | logger는 `results.csv`, `summary.json`을 찾는다. 1.8.0은 `metrics.jsonl`을 쓴다 | 상속한 logger가 `metrics.jsonl`, `weights/best.pt`를 올린다 |
| 4 | `Bad git executable` 경고가 나온다 | slim 이미지에 git이 없다 | 이미지에 git을 설치했다 |
| 5 | `LibreYOLO("yolox-s")`가 실패한다 | Python API는 가중치 경로를 받는다. 모델 ID는 CLI만 받는다 | 설정에 `weights` 경로를 둔다 |

> [!note] LibreYOLO 버전을 올릴 때
> 1번, 2번, 3번을 다시 확인한다. 고쳐졌으면 우회 코드를 지운다.

### 10.2 MLflow 서버 구성

```yaml
# compose.yaml에 추가할 서비스 안
mlflow:
  image: ghcr.io/mlflow/mlflow:<버전>
  command: >
    mlflow server --backend-store-uri sqlite:////mlflow/mlflow.db
    --artifacts-destination /mlflow/artifacts --host 0.0.0.0 --port 5000
  volumes:
    - ./outputs/mlflow:/mlflow
  ports:
    - "127.0.0.1:5000:5000"
```

- DB에 쓰는 프로세스는 서버 1개다. 학습을 여러 개 동시에 돌려도 SQLite가 충돌하지 않는다.
- 포트는 `127.0.0.1`에만 연다. 원격에서는 SSH 포트 포워딩으로 접속한다.
  예: `ssh -N -L 5000:127.0.0.1:5000 <계정>@<서버>`
- 서버 이미지 버전은 학습 쪽 `mlflow` 버전과 맞춘다.

## 11. 소프트웨어 아키텍처

```mermaid
flowchart TB
    subgraph Entry[실행 층 · scripts/]
      B1[build_raw_manifest]
      B2[propose_splits]
      B3[build_coco]
      TR[train]
    end
    subgraph Lib[라이브러리 층 · src/]
      D[data/*]
      subgraph TRL[training/]
        CK[checks]
        PV[provenance]
        TK[tracking]
        RN[runner]
      end
    end
    subgraph Cfg[설정 층 · configs/]
      CP[prep/]
      CD[data/]
      CT[train/]
    end
    subgraph Ext[외부]
      LY[LibreYOLO 1.8.0]
      MF[MLflow 서버<br/>compose 서비스]
      FS[(data/, outputs/)]
    end
    CP --> B1 & B2 & B3
    B1 & B2 & B3 --> D
    D --> FS
    B3 --> CD
    CT --> TR
    CD --> TR
    TR --> CK & PV & TK & RN
    RN --> LY
    TK --> LY
    TK --> MF
    LY --> FS
```

## 12. 정해야 할 것

- [x] MLflow 저장소: compose `mlflow` 서비스 + SQLite. artifact는 `outputs/mlflow/artifacts/` (2026-11-26).
- [x] 컨테이너 git: 설치한다 (2026-11-26, 커밋 `0a8a18b`).
- [ ] run 이름 규칙. 안: `<모델>_<데이터셋>`, 겹치면 `-vN`.
- [ ] 첫 기준 모델. 안: `yolox-s` (학습 확인됨).
- [ ] `configs/prep/common.yaml`을 공유할지.
- [ ] git 수정 상태에서 학습을 막을지, tag만 남길지.

관련 페이지: [libreyolo-models](libreyolo-models.md), [libreyolo-mlflow](libreyolo-mlflow.md), [libreyolo-dataset-formats](../../phase_0/concepts/libreyolo-dataset-formats.md)
