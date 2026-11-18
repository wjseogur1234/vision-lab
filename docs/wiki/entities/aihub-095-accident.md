---
type: entity
tags: [dataset, aihub, video, accident]
sources: []
created: 2026-11-16
updated: 2026-11-16
---

# AI Hub 095 — 교통사고 영상 데이터

차량과 보행자의 사고 영상이다. 상자 라벨이 없어서 검출 학습에는 쓰지 않는다.

> [!note] 근거
> 이 페이지의 수치는 2026-11-16에 원본 폴더를 직접 읽어서 얻었다. `raw/`에 ingest한 문서는 없다.

## 1. 위치와 용량

경로: `/mnt/data1/downloads/교통데이터/095.교통사고_영상_데이터/01.데이터/`
용량: 1.3GB.

받은 범위는 "차대보행자 / 영상 / 횡단보도"뿐이다.

## 2. 폴더 구조

```text
01.데이터/
├── 1.Training/
│   ├── 라벨링데이터_231108_add/
│   │   ├── TL_차대보행자_영상_횡단보도(신호등없음).zip
│   │   └── TL_차대보행자_영상_횡단보도(신호등있음).zip
│   └── 원천데이터_231108_add/
│       ├── TS_차대보행자_영상_횡단보도(신호등없음).zip
│       └── TS_차대보행자_영상_횡단보도(신호등있음).zip
└── 2.Validation/
    ├── 라벨링데이터_231108_add/   VL_... zip 2개
    └── 원천데이터_231108_add/     VS_... zip 2개
```

- 파일 이름의 앞 글자: `TL` Training 라벨, `TS` Training 원천, `VL` Validation 라벨, `VS` Validation 원천.
- zip 안에는 폴더가 없다. 파일이 바로 들어 있다.
- 영상 1개에 JSON 1개가 같은 이름으로 대응한다.
  예: `bb_1_210521_pedestrian_207_23110.mp4`, `bb_1_210521_pedestrian_207_23110.json`.

## 3. 규모

기준: zip 안의 파일 수.

| | 신호등 없음 | 신호등 있음 | 합계 |
|---|---|---|---|
| Training 영상 | 64개 (363MB) | 150개 (759MB) | 214개 |
| Validation 영상 | 8개 (33MB) | 18개 (94MB) | 26개 |

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
