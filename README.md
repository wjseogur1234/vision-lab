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
├── Dockerfile            # 실행 환경 이미지
├── compose.yaml          # 컨테이너 실행 설정 (GPU, 소스·데이터 마운트)
├── configs/
│   └── data/             # 데이터셋 YAML (LibreYOLO에 넘기는 파일)
├── src/
│   └── data/             # Phase 0 코드 (데이터셋 변환, 불러오기)
└── data/
    ├── raw/              # 원본으로 가는 심볼릭 링크 (git 제외)
    └── processed/        # 변환 결과로 가는 심볼릭 링크 (git 제외)
```

LibreYOLO는 고치지 않고 라이브러리로만 쓴다. 이 저장소에는 데이터 변환, 설정, 호출 코드만 둔다.

## 환경 구성

[uv](https://docs.astral.sh/uv/)를 쓴다.

```bash
uv sync
```

torch는 CUDA 12.8 빌드(`cu128`)를 받는다. 다른 GPU 환경에서는 `pyproject.toml`의 인덱스를 바꾼다.

### Docker

GPU를 쓰려면 호스트에 NVIDIA 드라이버와 NVIDIA Container Toolkit이 있어야 한다.

```bash
cp .env.example .env          # RAW_DATA_DIR에 원본 데이터 경로를 적는다
docker compose build
docker compose run --rm lab   # 컨테이너 안의 셸을 연다
```

소스는 `/app`에 마운트한다. 원본 데이터는 호스트와 같은 경로에 읽기 전용으로 마운트한다.

## 데이터

AI Hub `101.교통문제 해결을 위한 CCTV 교통 데이터(시내도로)`의 `교통안전(Bbox)`를 쓴다.
데이터는 저장소에 넣지 않는다. AI Hub에서 직접 받아 `data/raw/` 아래에 심볼릭 링크로 연결한다.
