---
type: entity
tags: [dataset, aihub, video, accident]
sources: []
created: 2026-11-16
updated: 2026-11-20
---

# AI Hub 095 — 교통사고 영상 데이터

차량과 보행자의 사고 영상이다. 상자 라벨이 없어서 검출 학습에는 쓰지 않는다.

> [!note] 근거
> 2026-11-20에 `data/raw/`의 파일을 확인했다.

## 1. 위치와 용량

접근 경로는 `data/raw/095.교통사고_영상_데이터/01.데이터/`다.
용량: 1.3GB.

받은 범위는 "차대보행자 / 영상 / 횡단보도"뿐이다.

## 2. 폴더 구조

각 분할에 `라벨링데이터_231108_add/`와
`원천데이터_231108_add/`가 있다.
그 아래에 신호등 유무별 폴더가 있다.

| 분할 | JSON 폴더 접두사 | MP4 폴더 접두사 |
|---|---|---|
| 1.Training | `TL_` | `TS_` |
| 2.Validation | `VL_` | `VS_` |

영상과 JSON은 확장자를 뺀 파일 이름으로 연결한다.

## 3. 규모

현재 풀려 있는 파일을 셌다.

| 분할 | MP4 | JSON |
|---|---:|---:|
| 1.Training | 214 | 214 |
| 2.Validation | 26 | 26 |

## 4. 라벨 JSON 형식

영상 단위의 사고 정보만 있다. 상자, 프레임 번호, 객체 위치는 없다.

```json
{
  "info": {"name": "accident"},
  "video": {
    "video_name": "bb_1_191008_pedestrian_125_193",
    "video_date": "191008",
    "filming_way": "bb",
    "video_point_of_view": "1",
    "accident_negligence_rateA": "70",
    "accident_negligence_rateB": "30",
    "accident_object": "1",
    "accident_place": "8",
    "accident_place_feature": "26",
    "vehicle_a_progress_info": "63",
    "vehicle_b_progress_info": "55"
  }
}
```

- 값은 대부분 숫자 코드다. 코드표는 받지 않았다.
- 파일마다 키가 조금 다르다. 과실 비율이 `accident_negligence_rate` 1개인 파일과 `...rateA`, `...rateB` 2개인 파일이 있다. `traffic_accident_type`은 일부 파일에만 있다.

> [!question] 촬영 방식
> `filming_way`의 `bb`는 블랙박스(차량 안 카메라)로 보인다. 확인하지 않았다.
> 맞다면 시점이 CCTV와 다르다.

## 5. 이 프로젝트에서의 쓰임

- 보행자 검출 학습에는 쓰지 않는다. 상자 라벨이 없다.
- 학습한 모델의 추론 결과를 눈으로 확인하는 영상으로 쓸 수 있다(Phase 2).

관련 데이터셋: [[aihub-101-cctv]], [[aihub-110-child-zone]]
