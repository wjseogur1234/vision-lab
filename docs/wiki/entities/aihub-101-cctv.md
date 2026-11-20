---
type: entity
tags: [dataset, aihub, cctv, bbox, tracking, segmentation]
sources: []
created: 2026-11-16
updated: 2026-11-20
---

# AI Hub 101 — 교통문제 해결을 위한 CCTV 교통 데이터(시내도로)

이 프로젝트의 주 데이터셋이다. 첫 과제(보행자 검출)에는 `교통안전(Bbox)`를 쓴다.
분할 방법은 [[dataset-split-plan]]에 적는다.

> [!note] 근거
> 2026-11-20에 `data/raw/`의 파일을 확인했다.

## 1. 위치와 용량

접근 경로는 `data/raw/101.교통문제_해결을_위한_CCTV_교통_데이터(시내도로)/01.데이터/`다.
원본 폴더는 읽기만 한다.

전체 디스크 사용량은 336 GiB다(`du -shL` 기준).

## 2. 폴더 구조

두 분할에 Bbox, Tracking, Segmantation이 있다.
`Segmantation`은 원본 폴더 이름이다.

| 종류 | Bbox 폴더 내 경로 |
|---|---|
| 이미지 | `2.원천데이터/<장소 폴더>/<장소>/<카메라ID>/*.jpg` |
| 라벨 | `1.라벨링데이터_230510_add/1.라벨링데이터/<장소>/<카메라ID>/*.json` |

경로에는 장소 이름이 두 번 나올 수 있다.
Training Tracking에는 `2.원천데이터_230522_add/`도 있다.
Validation Tracking 라벨은 장소 폴더 없이 카메라 폴더에 있다.

### 2.1 실제 파일 수

| 하위 데이터 | Training JPG / JSON | Validation JPG / JSON |
|---|---:|---:|
| Bbox | 145,694 / 70 | 18,211 / 45 |
| Tracking | 286,199 / 6 | 23,546 / 1 |
| Segmantation | 24,691 / 61 | 1,028 / 39 |

Training Tracking JPG 수는 추가분 31,200장을 포함한다.

## 3. 교통안전(Bbox)

### 3.1 규모

기준: 라벨 JSON에 등록된 수. 실제 파일 수는 2.1절에 있다.

| | Training | Validation |
|---|---|---|
| 장소 | 37곳 | 30곳 |
| 카메라 | 70대 | 45대 |
| 이미지 | 145,701장 | 18,212장 |
| 보행자가 있는 이미지 | 69,230장 | 8,340장 |
| 전체 상자 | 1,662,454개 | 225,357개 |
| 보행자 상자 | 247,269개 | 31,294개 |
| 촬영 구간(`meta`) | 2,986개 | 1,526개 |

- Validation의 카메라 45대는 모두 Training에도 있다. 이 점이 분할 방법을 정한다. ([[dataset-split-plan]] 2절)
- 카메라 1대의 이미지 수(Training): 최소 1장, 중앙값 1,928장, 최대 7,064장.

### 3.2 클래스

| ID | 이름 | Training 상자 | Validation 상자 |
|---|---|---|---|
| 1 | 승용차 | 1,140,186 | 156,113 |
| 2 | 소형버스 | 5,357 | 644 |
| 3 | 대형버스 | 70,421 | 9,001 |
| 4 | 트럭 | 162,683 | 24,096 |
| 5 | 대형 트레일러 | 1,736 | 106 |
| 6 | 오토바이(자전거) | 34,802 | 4,103 |
| 7 | 보행자 | 247,269 | 31,294 |
| 8 | 분류없음 | 0 | 0 |

### 3.3 라벨 JSON 형식

COCO와 비슷하지만 표준과 다르다. 최상위 키는 `info`, `images`, `annotations`, `categories`, `guideline`, `meta`다.

```json
{
  "images": [
    {"id": 369411, "file_name": "BC2000201/20201017_140001_S_23166.jpg",
     "meta_id": 3237, "frame_value": 23166}
  ],
  "annotations": [
    {"id": 369411, "image_id": 369411,
     "bbox": [[1058.2, 355.3, 1110.9, 399.4], [626.2, 533.1, 660.8, 625.0]],
     "category_id": [1, 7],
     "tracking_id": [], "segmentation": [], "area": 0.0, "iscrowd": "Y"}
  ],
  "categories": [{"id": 7, "name": "보행자"}],
  "meta": [
    {"id": 3221, "camera_id": "BC2000201", "date": "2020-10-14", "time": "1:59:58",
     "weather": "Sunny", "time_space": "새벽", "resolution": "FHD", "fps": 10}
  ]
}
```

표준 COCO와 다른 점:

| 항목 | 이 데이터 | 표준 COCO |
|---|---|---|
| `annotations` 1개 | 이미지 1장의 상자 전체 | 상자 1개 |
| `bbox` | 상자 목록. 상자는 `[x1, y1, x2, y2]` 픽셀 | `[x, y, w, h]` |
| `category_id` | 목록. `bbox`와 순서가 같다 | 숫자 1개 |
| `images`의 `width`, `height` | 없다 | 있다 |

- 이미지 크기가 라벨에 없다. YOLO 형식으로 바꾸려면 이미지 파일에서 크기를 읽어야 한다.
- 좌표가 이미지 밖으로 나간 예가 있다. 높이 1080인 이미지에서 `y2 = 1085.77`이 나왔다.
- `images[].meta_id`가 `meta[].id`를 가리킨다.

> [!question] `guideline`
> 좌표 목록이 들어 있다. 예: `[[0.0, 0.0, 0.0, 244.0, 1920.0, 248.0, 1920.0, 0.0, 0.0, 0.0]]`.
> 라벨링에서 제외한 영역으로 보인다. 확인하지 않았다.

### 3.4 촬영 조건 (`meta`)

기준: 촬영 구간(`meta`) 수.

| 항목 | Training | Validation |
|---|---|---|
| 날씨 | Sunny 2,193 / Rainy 451 / Cloudy 236 / Foggy 53 / Snow 53 | Sunny 1,212 / Rainy 209 / Cloudy 86 / Foggy 19 |
| 시간대 | 오전 997 / 낮 856 / 오후 792 / 새벽 341 | 오전 502 / 낮 438 / 오후 388 / 새벽 198 |
| 해상도 | FHD 1,823 / HD 1,161 / 빈 값 2 | FHD 1,067 / HD 459 |

`meta`에는 `week_day`, `crosswalk`, `blocked`, `height`, `light`, `lines`, `direction`, `road_type`, `address`도 있다.

### 3.5 보행자 상자의 크기

기준: 상자 높이(픽셀), 원본 해상도.

| 분위 | Training | Validation |
|---|---|---|
| 10% | 24.6 | 24.6 |
| 50% | 49.9 | 44.5 |
| 90% | 128.4 | 116.5 |

보행자가 작다. 학습 입력 크기가 성능에 크게 영향을 줄 것이다.

## 4. 교통안전(Tracking)

- `tracking_id`가 있는 연속 프레임이다.
- Validation 라벨에는 이미지 37,200장이 등록돼 있다.
- Validation에 실제 JPG는 23,546장 있다.
- 2026-11-16에는 이전 경로의 원천 ZIP이 열리지 않았다.

## 5. 교통안전(Segmantation)

- `bbox`는 비어 있다.
- `segmentation`에 다각형 좌표가 있다.
- Validation 라벨에는 이미지 3,087장이 등록돼 있다.

## 6. 이 프로젝트에서의 쓰임

| 하위 데이터 | 쓰임 |
|---|---|
| Bbox | Phase 0~3의 보행자 검출에 쓴다 |
| Tracking | Phase 4(vision task 확장)의 후보다 |
| Segmantation | Phase 4(vision task 확장)의 후보다 |

관련 데이터셋: [[aihub-095-accident]], [[aihub-110-child-zone]]
