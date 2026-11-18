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
├── compose.yaml          # 컨테이너 실행 설정 (환경별 마운트, GPU)
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

[uv](https://docs.astral.sh/uv/)를 쓴다.

환경은 2개다. 의존성 그룹으로 나눈다.

| 환경 | 하는 일 | 의존성 그룹 | GPU |
|---|---|---|---|
| 전처리 | 원본을 거르고 YOLO 형식으로 변환한다 | `prep` | 안 씀 |
| 학습 | LibreYOLO로 학습하고 추론한다 | `train` | 씀 |

```bash
uv sync --group prep     # 전처리 환경
uv sync --group train    # 학습 환경
```

torch는 CUDA 12.8 빌드(`cu128`)를 받는다. 다른 GPU 환경에서는 `pyproject.toml`의 인덱스를 바꾼다.

### Docker

환경마다 서비스가 하나씩 있다.
학습 환경에서 GPU를 쓰려면 호스트에 NVIDIA 드라이버와 NVIDIA Container Toolkit이 있어야 한다.

```bash
cp .env.example .env            # RAW_DATA_DIR에 원본 데이터 경로를 적는다
docker compose build
docker compose run --rm prep    # 전처리 환경의 셸을 연다
docker compose run --rm train   # 학습 환경의 셸을 연다
```

| 마운트 | 전처리 (`prep`) | 학습 (`train`) |
|---|---|---|
| 소스 (`/app`) | 쓰기 가능 | 쓰기 가능 |
| 원본 데이터 | 읽기 전용 | 마운트 안 함 |
| `data/processed/` | 쓰기 가능 | 읽기 전용 |

원본 데이터는 호스트와 같은 경로에 마운트한다.
학습 환경은 전처리 결과만 읽는다.

## 데이터

AI Hub `101.교통문제 해결을 위한 CCTV 교통 데이터(시내도로)`의 `교통안전(Bbox)`를 쓴다.
데이터는 저장소에 넣지 않는다. AI Hub에서 직접 받아 `data/raw/` 아래에 심볼릭 링크로 연결한다.
