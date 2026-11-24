---
type: analysis
tags: [dataset, manifest, preprocessing]
sources: ["wiki/phase_0/entities/aihub-095-accident.md", "wiki/phase_0/entities/aihub-101-cctv.md", "wiki/phase_0/entities/aihub-110-child-zone.md"]
created: 2026-11-24
updated: 2026-11-24
---

# 원본 manifest — AI Hub 095·101·110

`data/raw/`의 원본 파일과 라벨을 연결한다.
AI Hub의 원본 분할을 `source_split`에 기록한다.
학습용으로 나눈 결과는 [분할 계획 5.4절](dataset-split-plan.md#54-결과-구조)을 참고한다.

## 생성

프로젝트 루트에서 실행한다.

```bash
docker compose run --rm lab python -m data.raw_manifest
```

결과는 `data/interim/raw-manifests/<번호>/manifest.csv`에 저장한다.
`--dataset 101`을 붙이면 101만 처리한다.
입력 경로와 매칭 규칙은 [생성 코드](../../../../src/data/raw_manifest.py)에 있다.

| 데이터셋 | 대상 | 매칭 기준 |
|---|---|---|
| [095](../entities/aihub-095-accident.md) | MP4와 사고 JSON | 원본 분할과 확장자를 뺀 파일명 |
| [101](../entities/aihub-101-cctv.md) | Bbox의 JPG와 JSON 이미지 항목 | 원본 분할, 장소, 카메라, JPG 파일명 |
| [110](../entities/aihub-110-child-zone.md) | JPG 프레임과 XML | 원본 분할, 추가분, 행동 폴더, 영상 폴더, 확장자를 뺀 파일명 |

## CSV 열과 확인 방법

| 열 | 기록 내용 |
|---|---|
| `source_split`, `batch` | 원본 분할과 추가분. 기본 묶음의 `batch`는 빈 값이다. |
| `media_type` | 이미지 또는 영상 |
| `file_name`, `label_file` | 각 데이터셋 폴더 기준 원본과 라벨의 상대 경로 |
| `label_image_id` | 101 JSON의 `images[].id` |
| `match_status` | 원본과 라벨의 대응 상태 |
| `location`, `camera` | 101의 장소와 카메라 |
| `action`, `video_id` | 110의 행동 폴더와 영상 이름. 095는 영상 이름만 기록한다. |
| `weather`, `time_of_day` | 101 라벨의 날씨와 시간대. 값이 없으면 `unknown`으로 기록한다. |
| `width`, `height` | JPG에서 읽은 픽셀 크기 |
| `num_persons` | 원본 보행자 라벨 수. 집계할 상자 라벨이 없으면 비워 둔다. |

| `match_status` | 의미 | 확인 방법 |
|---|---|---|
| `matched` | 원본과 라벨이 1대1로 연결됨 | 두 경로를 확인한다. |
| `missing_media` | 라벨에 대응하는 원본을 찾지 못함 | `label_file`을 확인한다. 101은 `label_image_id`로 JSON의 JPG 이름을 찾는다. |
| `missing_label` | 원본에 대응하는 라벨을 찾지 못함 | `file_name`으로 원본 경로를 확인한다. |
| `ambiguous` | 원본 또는 라벨 후보가 여러 개임 | 후보마다 한 행이 생긴다. 원본과 라벨 경로를 대조한다. |

## 2026-11-24 생성 결과

수치는 생성한 CSV의 `match_status`별 행 수다.

| 데이터셋 | `matched` | `missing_media` | `missing_label` | `ambiguous` |
|---|---:|---:|---:|---:|
| 095 | 240 | 0 | 0 | 0 |
| 101 Bbox | 163,901 | 4 | 0 | 12 |
| 110 | 84,600 | 45,973 | 30,301 | 0 |

101 Bbox의 후보 중복 12행은 JPG 4개와 라벨 항목 8개다.
다음 JPG 4개는 라벨에 적힌 이름이다.

| 원본 분할 | JPG 이름 | 라벨 이미지 ID |
|---|---|---:|
| Training | `SC0004601/20200908_060002_S_10950.jpg` | 217332 |
| Training | `SC0013302/20200907_130003_R_9450.jpg` | 226498 |
| Training | `SC0013302/20200909_060000_R_2700.jpg` | 226600 |
| Validation | `BC1000701/20201010_170000-200035_S_90830.jpg` | 283435 |

110은 원본 JPG 114,901개 중 84,600개(73.6%)를 연결했다.

| 110 묶음 | 일치 | JPG 대응 없음 | XML 대응 없음 |
|---|---:|---:|---:|
| 기본 | 19,500 | 38,102 | 27,900 |
| `0708_add` | 2,100 | 7,500 | 2,100 |
| `0915_add` | 63,000 | 371 | 301 |

110의 불일치는 기본 묶음에 가장 많다.
실제 누락과 이름 차이는 원본 경로를 대조해야 구분할 수 있다.
