# vision-lab

[LibreYOLO](https://github.com/LibreYOLO/libreyolo)로 vision AI 모델을 학습하는 프로젝트다.
첫 과제는 CCTV 영상의 보행자 검출이다.

## 진행 단계

| 단계 | 내용 | 코드 위치 | 상태 |
|---|---|---|---|
| 준비 | 프로젝트 구성, 라이브러리 환경 | `pyproject.toml` | 진행 중 |
| Phase 0 | 데이터셋 구조, 데이터셋 불러오기 | `src/data/` | 예정 |

## 폴더

```text
.
├── pyproject.toml        # 의존성. LibreYOLO(PyPI)와 torch CUDA 빌드를 지정한다
├── Dockerfile            # 실행 환경 이미지 (전처리, 학습)
├── compose.yaml          # 컨테이너 실행 설정 (마운트, GPU)
├── configs/
│   └── data/             # 데이터셋 YAML (LibreYOLO에 넘기는 파일)
├── src/
│   └── data/             # Phase 0 코드 (데이터셋 변환, 불러오기)
└── data/
    ├── raw/              # 원본으로 가는 심볼릭 링크 (git 제외)
    ├── interim/          # 전처리 중간 파일. 지워도 된다 (git 제외)
    └── processed/        # 변환 결과로 가는 심볼릭 링크 (git 제외)
```

LibreYOLO는 고치지 않고 라이브러리로만 쓴다. 이 저장소에는 데이터 변환, 설정, 호출 코드만 둔다.

## 환경 구성

전처리, 학습, 추론은 Docker 서비스 `lab`에서 실행한다.
호스트에는 NVIDIA 드라이버와 NVIDIA Container Toolkit이 필요하다.

### 의존성

[uv](https://docs.astral.sh/uv/)로 의존성을 관리한다.
빌드할 때 `uv.lock`에 따라 `prep`, `train`, `dev` 그룹을 함께 설치한다.
호스트에서 `uv sync`를 실행하지 않아도 된다.

- 가상환경은 컨테이너의 `/opt/venv`에 있다. `PATH`에 들어 있으므로 `python`을 바로 실행한다.
- 의존성을 바꾸면 `pyproject.toml`을 고치고 `uv lock`을 실행한다. 그다음 이미지를 다시 빌드한다(`--build`).
- torch는 CUDA 12.8 빌드(`cu128`)를 받는다. 다른 GPU 환경에서는 `pyproject.toml`의 인덱스를 바꾼다.

### 실행

```bash
cp .env.example .env            # RAW_DATA_DIR에 원본 데이터 경로를 적는다
docker compose build
docker compose run --rm lab
```

`run`은 빌드한 이미지를 재사용한다.
실행할 때마다 새 컨테이너를 만든다.
셸에서 `exit`를 실행하면 컨테이너가 삭제된다.

컨테이너를 유지하면서 작업할 수도 있다.
다음 명령은 `lab`을 시작하고 셸을 연다.

```bash
docker compose up -d lab
docker compose exec lab bash
```

다른 터미널에서도 `exec` 명령으로 셸을 열 수 있다.
`exit`를 실행하면 해당 셸만 종료된다.
작업이 끝나면 컨테이너를 중지한다.

```bash
docker compose stop lab
```

`run`으로 만든 컨테이너에 접속하려면 이름을 확인한다.

```bash
docker compose ps -a
docker exec -it <컨테이너_이름> bash
```

프로젝트 폴더에 저장한 파일은 컨테이너가 삭제돼도 남는다.
컨테이너 내부의 다른 위치에 저장한 파일은 삭제될 수 있다.

| 마운트 | 접근 권한 |
|---|---|
| 프로젝트 폴더 (`/app`, `data/` 포함) | 쓰기 가능 |
| 원본 데이터 (`RAW_DATA_DIR`) | 읽기 전용 |

원본 데이터는 호스트와 같은 경로에 마운트한다.
그래서 `data/raw/`의 심볼릭 링크가 컨테이너 안에서도 맞는다.
마운트 설정을 바꾼 뒤에는 컨테이너를 다시 만들어야 한다.

## 데이터

AI Hub `101.교통문제 해결을 위한 CCTV 교통 데이터(시내도로)`의 `교통안전(Bbox)`를 쓴다.
데이터는 저장소에 넣지 않는다. AI Hub에서 직접 받아 `data/raw/` 아래에 심볼릭 링크로 연결한다.

### 원본 manifest

데이터셋마다 원본 파일과 라벨의 대응을 CSV로 기록한다.

```bash
docker compose run --rm lab python -m data.raw_manifest
docker compose run --rm lab python -m data.raw_manifest --dataset 101
```

기본 결과 경로는 `data/interim/raw-manifests/<데이터셋 번호>/manifest.csv`다.
`--output-dir`로 결과 경로를 바꿀 수 있다.
파일 경로는 각 원본 데이터셋 폴더를 기준으로 기록한다.

- `095`는 MP4와 사고 JSON을 연결한다.
- `101`은 Bbox JPG와 JSON의 이미지 항목을 연결한다.
- `110`은 JPG 프레임과 XML을 연결한다.
- `source_split`에는 AI Hub의 원본 분할을 기록한다.
- `num_persons`에는 원본 보행자 라벨 수를 기록한다.
- 라벨이 없거나 보행자 상자 라벨이 없는 데이터셋은 수를 비워 둔다.
- 짝이 없는 파일과 후보가 여러 개인 파일도 `match_status`에 기록한다.
