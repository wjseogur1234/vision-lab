---
type: analysis
tags: [libreyolo, mlflow, experiment-tracking]
sources: ["wiki/sources/libreyolo-model-reference.md"]
created: 2026-11-24
updated: 2026-11-24
---

# LibreYOLO MLflow 연동

LibreYOLO의 MLflow 지원 여부와 도입 방법을 조사했다.
기록 규격은 아직 정하지 않았다.

> [!note] 근거 (2026-11-24)
> 설치된 `libreyolo==1.8.0` 코드와 [Experiment loggers 문서](https://www.libreyolo.com/docs/train/loggers)를 확인했다.
> 문서는 "Verified against LibreYOLO v1.6.0"이라고 적는다.

## 1. 지원 여부

- LibreYOLO는 `MLflowLogger`를 제공한다. 코드 위치는 `libreyolo/training/loggers/mlflow_logger.py`다.
- 다른 logger도 있다: `tensorboard`, `wandb`, `comet`, `clearml`, `neptune`, `dvclive`.
- 현재 컨테이너에는 `mlflow` 패키지가 없다. `uv.lock`에도 없다.
- 설치하려면 `libreyolo[mlflow]` extra를 쓴다.

## 2. 사용 방법

CLI에는 logger 옵션이 없다. `libreyolo train --help`에는 `--log-interval`만 있다.
그래서 Python API로 학습한다.

```python
from libreyolo.training import MLflowLogger

model.train(
    data="configs/data/aihub101-ped-mini.yaml",
    epochs=1,
    loggers=[MLflowLogger(
        tracking_uri="sqlite:///mlflow.db",
        experiment_name="aihub101-ped",
        run_name="yolox-s_mini",
        log_artifacts=True,
        log_checkpoints=False,
    )],
)
```

- `loggers="mlflow"`처럼 이름만 써도 된다.
- `tracking_uri`를 생략하면 `MLFLOW_TRACKING_URI` 환경 변수를 쓴다.
- MLflow 3.x에서 로컬 `./mlruns`를 쓰려면 `MLFLOW_ALLOW_FILE_STORE=true`가 필요하다.
- `log_checkpoints=True`면 `weights/best.pt`도 올린다.

## 3. 기록되는 항목

| 종류 | 내용 | 시점 |
|---|---|---|
| params | 학습 설정 전체 | 학습 시작 |
| metrics | `train/loss`, `train/loss/<구성 요소>`, `lr/<그룹>`, `val/<지표>`, `time/epoch_seconds` | epoch마다. step은 1부터 시작 |
| artifacts | `results.csv`, `train_config.yaml`, `summary.json` | 학습 끝 |
| run 이름 | 기본값 `<계열><크기>-<작업>`. 예: `yoloxs-detect` | 학습 시작 |

- 검증 결과 그림은 올리지 않는다.
- 학습 중에 logger가 실패하면 그 logger만 꺼진다. 학습은 계속된다.
- 실패한 학습은 run 상태를 `FAILED`로 닫는다.

## 4. 기록되지 않는 항목

다음 항목은 직접 추가해야 한다.

| 항목 | 예 | 필요한 이유 |
|---|---|---|
| 데이터 출처 | `metadata.yaml`, 분할 파일 해시, `fraction`, 배경 비율 | 분할과 배경 비율이 바뀔 수 있다 |
| 코드 출처 | git 커밋, 수정된 파일 여부 | 결과를 다시 만들 수 있어야 한다 |

추가 방법은 두 가지다.

- `callbacks`의 `on_train_start`에서 `mlflow.set_tags()`를 호출한다.
- `MLflowLogger`를 상속해 시작할 때 tag를 추가한다.

`callbacks`는 함수 또는 `on_train_start`, `on_train_epoch_end`, `on_train_end`, `on_train_exception`을 가진 객체를 받는다.
앞의 세 hook에서 난 예외는 학습을 끝낸다.

## 5. 도입할 때 할 일

1. `pyproject.toml`의 `train` 그룹에 `libreyolo[mlflow]`를 추가한다. 이미지를 다시 빌드한다.
2. CLI 대신 쓸 학습 스크립트를 만든다. 이 스크립트가 데이터·코드 출처 tag를 붙인다.
3. tracking 저장소와 artifact 위치를 정한다.
4. UI를 쓰려면 `compose.yaml`에 포트를 연다.

## 6. 정해야 할 것

- [ ] tracking 저장소: 로컬 파일, SQLite, 별도 서버.
- [ ] artifact 위치. 현재 학습 결과는 임시로 `outputs/runs/`에 있다.
- [ ] experiment와 run 이름 규칙.
- [ ] tag 목록. 예: `phase`, `purpose`(smoke, baseline, ablation).
- [ ] `smoke-mini` 결과를 MLflow에 다시 올릴지.

규격이 정해지면 `requirements/`에 기록 규격 페이지를 만든다. 이 페이지가 그 근거가 된다.

> [!question] `libreyolo monitor`
> run 파일을 읽어 보여 주는 읽기 전용 대시보드다. MLflow를 대신하지 못한다. 쓰임은 확인하지 않았다.

관련 페이지: [libreyolo-models](libreyolo-models.md), [분할 계획 8.2절](dataset-split-plan.md#82-학습-확인)
