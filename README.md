# vision-lab

## 환경 구성

```bash
cp .env.example .env            # RAW_DATA_DIR에 원본 데이터 경로를 적는다
docker compose build
```

호스트에 NVIDIA 드라이버와 NVIDIA Container Toolkit이 필요하다.

## 데이터셋 만들기

```bash
docker compose run --rm lab python scripts/<파일명>.py [키=값 ...]
```

`<파일명>`은 아래 순서로 실행한다.

1. `build_raw_manifest`
2. `propose_splits`
3. `build_coco`

```bash
# 예
docker compose run --rm lab python scripts/build_raw_manifest.py dataset=[101]
docker compose run --rm lab python scripts/propose_splits.py
docker compose run --rm lab python scripts/build_coco.py name=aihub101-ped-v3 data@split_plan=aihub101-ped-v2.splits
```

설정은 `configs/prep/<파일명>.yaml`에 있다. `--cfg job`을 붙이면 최종 설정을 보여 준다.

## 학습

```bash
docker compose run --rm lab libreyolo train --data configs/data/<데이터셋>.yaml \
  --model <모델> --cache false --project outputs/runs --name <실행 이름> [옵션 ...]
```

```bash
# 예
docker compose run --rm lab libreyolo train --data configs/data/aihub101-ped-mini.yaml \
  --model yolox-s --cache false --project outputs/runs --name smoke-mini --epochs 1
```

`<데이터셋>`은 `build_coco`가 만든 이름이다.

`--cache disk`는 쓰지 않는다. 원본이 읽기 전용이라 실패한다.
