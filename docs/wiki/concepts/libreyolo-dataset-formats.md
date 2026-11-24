---
type: concept
tags: [libreyolo, dataset, annotation]
sources: ["wiki/sources/libreyolo-model-reference.md"]
created: 2026-11-21
updated: 2026-11-24
---

# LibreYOLO 데이터셋 형식

사용자가 제공한 공식 데이터셋 규격을 정리했다.
[공식 데이터 형식 문서](https://www.libreyolo.com/docs/reference/dataset-formats)도 참고한다.
제공 자료는 `dataset_schema.md`의 v1.6.0을 기준으로 밝힌다.
프로젝트는 `libreyolo==1.8.0`을 지정한다.
버전 차이는 실제 설치 환경에서 확인해야 한다.
1.8.0에서 COCO JSON 검출 학습은 동작을 확인했다(2026-11-24, YOLOX). [분할 계획 8절](../analyses/dataset-split-plan.md#8-mini-검증-결과-2026-11-24)
각 형식의 존재가 모든 모델의 학습 지원을 뜻하지는 않는다.
[모델별 검출 데이터 형식](../analyses/libreyolo-models.md#모델별-검출-데이터-형식)을 함께 확인한다.

## 공통 YAML

`detect`, `segment`, `pose`, `obb`에 적용한다.

| 키 | 필요 여부 | 의미 |
|---|---|---|
| `path` | 선택 | 데이터셋 루트 |
| `train` | 학습 시 필요 | 학습 이미지 경로 |
| `val` | 검증 시 필요 | 검증 이미지 경로 |
| `test` | 선택 | 테스트 이미지 경로 |
| `names` | 필요 | 클래스 목록 또는 정수 키 매핑 |
| `nc` | 선택 | 클래스 수. `names`와 일치해야 한다 |
| `download` | 선택 | 다운로드 지침. Python 스크립트는 명시적 허용이 필요하다 |
| `annotations` | 선택 | 분할별 COCO JSON. 검출, 인스턴스 분할, OBB에 사용한다 |
| `channels` | 선택 | RGB는 3이 기본값. 회색조는 1. 2는 이벤트 히스토그램용으로 예약됨 |

`train`, `val`, `test`는 이미지 폴더를 받을 수 있다.
이미지 목록 `.txt`나 이들의 목록도 받을 수 있다.
일반 텍스트 라벨 경로는 다음과 같이 대응한다.

```text
images/train/image.jpg → labels/train/image.txt
```

COCO JSON은 분할별 주석 파일을 지정한다.
분할 경로는 해당 이미지의 루트다.

```yaml
path: dataset
train: images/train
val: images/val
annotations:
  train: annotations/train.json
  val: annotations/val.json
names:
  0: person
```

`names`가 있으면 COCO의 클래스 이름과 일치해야 한다.
`names`가 모델의 클래스 ID를 결정한다.
`names`가 없으면 COCO ID를 정렬해 0부터 연속된 ID로 바꾼다.
데이터셋 YAML에는 `task` 키를 넣지 않는다.
명시적으로 선택한 모델과 작업이 우선한다.

`channels: 1`은 이미지를 읽을 때 회색조로 바꾼다.
학습, 검증, 추론에 모두 적용한다.
지원 모델은 YOLO9, YOLO9-E2E, YOLO9-P2, YOLOv7, YOLOX, YOLO-NAS, RTMDet, PP-YOLOE, PicoDet, D-FINE, DEIM, DEIMv2, RT-DETR, RT-DETRv2, RT-DETRv4, RF-DETR, EC, FOMO다.
다른 모델은 `ValueError`를 낸다.

## 텍스트 라벨 공통 규칙

- 이미지마다 `.txt` 라벨 파일을 둔다.
- 라벨 파일이 없거나 비어 있으면 객체가 없는 이미지로 처리한다.
- `class_id`는 `0..nc-1` 범위의 정수다.
- 좌표는 원본 이미지 크기 기준으로 정규화한다.
- 좌표는 `0..1` 범위의 유한한 실수다.
- 라벨에는 신뢰도와 추적 ID를 넣지 않는다.

### detect — 객체 검출

```text
<class_id> <cx> <cy> <w> <h>
```

한 줄에 필드 5개를 쓴다.
중심점과 크기는 축에 평행한 박스를 나타낸다.
`w`와 `h`는 양수다.
이 프로젝트의 변환 계획은 [분할 계획 5.3절](../analyses/dataset-split-plan.md#53-라벨-변환)에 있다.

### segment — 인스턴스 분할

```text
<class_id> <x1> <y1> ... <xN> <yN>
```

다각형에는 점이 3개 이상 필요하다.
좌표의 개수는 짝수여야 한다.
퇴화한 다각형은 허용하지 않는다.
필드가 5개인 검출 박스도 받는다.
이 경우 직사각형 분할로 처리한다.

### pose — 자세 추정

```text
<class_id> <cx> <cy> <w> <h> <k1x> <k1y> [<k1v>] ... <kKx> <kKy> [<kKv>]
```

YAML에 `kpt_shape: [K, D]`가 필요하다.
`D`는 2 또는 3이다.
필드 수는 정확히 `5 + K * D`다.
관절점 좌표는 정규화한다.
가시성 `v`는 있으면 0, 1 또는 2다.
선택 항목 `flip_idx`는 `0..K-1`의 정수 순열이다.
RF-DETR 다중 클래스 데이터에는 `names`가 필요하다.
클래스별 `kpt_names`는 선택 사항이다.
빈 관절점 이름 목록은 박스 전용 클래스를 뜻한다.
최소 한 클래스에는 관절점이 있어야 한다.

### obb — 회전 박스

```text
<class_id> <x1> <y1> <x2> <y2> <x3> <y3> <x4> <y4>
```

한 줄에 필드 9개를 쓴다.
네 점은 면적이 있는 회전 직사각형을 이룬다.
점 좌표는 `0..1`로 정규화한다.
라벨 파일에는 각도를 저장하지 않는다.
파서는 기본적으로 범위 밖 좌표를 거부한다.
데이터셋과 검증 로더는 유효한 경계 박스를 잘라낼 수 있다.
잘라낸 후 퇴화한 박스는 거부한다.
9개 필드는 작업에 따라 해석이 다르다.
`segment`에서는 네 점 다각형일 수 있다.

내부 표현은 `xywhr`다.
각도는 너비 방향의 회전을 라디안으로 나타낸다.
결과 행은 `xywhr, conf, cls`를 노출한다.
COCO JSON은 다음 순서로 주석을 찾는다.

1. `obb`의 픽셀 좌표 점 8개
2. `obb`의 `[cx, cy, w, h, angle]`. 각도는 라디안
3. COCO `segmentation` 다각형 또는 RLE. 최소 면적 직사각형으로 변환
4. COCO `bbox`. 축에 평행한 박스로 읽어 변환

OBB 학습에서는 mosaic과 mixup을 끈다.
점 좌표를 고려한 증강이 아직 없기 때문이다.

## 픽셀 단위 작업

### semantic — 의미 분할

이미지마다 같은 해상도의 단일 채널 마스크가 필요하다.
일반적으로 무손실 PNG를 쓴다.
경로는 `images`를 `masks_dir`로 바꿔 찾는다.
`masks_dir`의 기본값은 `masks`다.
팔레트 PNG는 팔레트 인덱스를 읽는다.
픽셀 값 `0..nc-1`은 클래스 ID다.
값 `255`는 무시하며 손실과 지표에서 제외한다.
`label_mapping`은 원본 ID를 학습 ID로 바꾼다.
매핑되지 않은 원본 ID는 무시한다.
학습 ID는 `0..nc-1` 범위여야 한다.

`masks_dir`을 생략하면 다각형 라벨을 마스크로 변환한다.
객체 클래스 뒤에 `background` 클래스도 추가한다.
이때 `nc`가 1 증가한다.

### panoptic — 파놉틱 분할

COCO-panoptic 형식을 그대로 쓴다.
이미지마다 같은 해상도의 RGB PNG가 필요하다.
색상은 `segment_id = R + 256 * G + 256 * 256 * B`로 해석한다.
세그먼트는 겹치지 않는다.
ID 0인 검은색은 미라벨 영역이다.
미라벨 영역은 지표에서 제외한다.
JSON의 `annotations[].file_name`은 PNG를 가리킨다.
`segments_info[].id`는 PNG의 세그먼트 ID와 일치한다.
`iscrowd`는 군집 영역을 표시한다.
군집 영역은 거짓 음성이 아니다.
군집 영역 대부분과 겹친 예측도 거짓 양성이 아니다.
`isthing`은 `segments_info`가 아닌 `categories`의 속성이다.

COCO의 원본 클래스 ID는 연속되지 않을 수 있다.
클래스 이름을 통해 YAML의 연속된 ID로 매핑한다.
JSON 클래스가 `names`에 없으면 오류가 난다.
`annotations`와 `panoptic_dir`은 경로 하나를 받을 수 있다.
분할별 경로 매핑도 받을 수 있다.
검증은 정답 해상도에서 PQ를 계산한다.
나타난 클래스의 평균과 `PQ_things`, `PQ_stuff`를 보고한다.
같은 클래스의 예측과 정답은 일대일로 매칭한다.
IoU가 0.5보다 커야 매칭한다.

### depth — 깊이

이미지마다 같은 해상도의 단일 채널 깊이 맵이 필요하다.
PNG, TIF 또는 `.npy`를 쓴다.
값은 데이터셋 전체에서 같은 깊이 단위를 쓴다.
0, 음수, NaN, 무한대는 유효하지 않은 픽셀이다.
해당 픽셀은 손실과 지표에서 제외한다.

| YAML 키 | 기본값 | 의미 |
|---|---|---|
| `depths_dir` | `depths` | 깊이 맵 폴더 |
| `depth_stem_suffix` | 없음 | 이미지 이름 뒤에 붙일 접미사. 생략 시 같은 이름과 `_depth`를 시도한다 |
| `depth_mask_suffix` | `_mask` | 유효성 마스크 접미사 |
| `depth_scale` | `256.0` | 정수형 깊이 맵의 나눗수 |

마스크의 0 이하, NaN, 무한대는 유효하지 않다.
부동소수점 `.npy`는 `depth_scale` 없이 쓴다.

### edge — 경계

RGB 이미지마다 같은 해상도의 단일 채널 맵을 쓴다.
맵은 PNG 또는 TIF여야 한다.
RGB 시각화 이미지는 쓰지 않는다.
정수 맵은 자료형의 최댓값으로 나눈다.
실수 맵은 유한한 `0..1` 값이어야 한다.
0은 비경계, 1은 경계다.
선택 마스크의 0이 아닌 값은 유효하다.
리사이즈에는 최근접 보간을 쓴다.
패딩 픽셀은 검증에서 제외한다.

| YAML 키 | 기본값 | 의미 |
|---|---|---|
| `edges_dir` | `edges` | 경계 맵 폴더 |
| `edge_stem_suffix` | 없음 | 이미지 이름 접미사 |
| `edge_extension` | `.png` | 무손실 라벨 확장자 |
| `edge_invert` | 꺼짐 | 흰 배경의 검은 경계를 반전 |
| `masks_dir` | `masks` | 선택 유효성 마스크 폴더 |

검증은 비최대 억제 후 ODS와 OIS F-measure를 보고한다.
픽셀은 일대일로 매칭한다.
허용 거리는 `edge_max_dist * 이미지 대각선`이다.
기본 정규화 허용치는 0.0075다.
로더는 벤치마크 데이터를 배포하거나 다운로드하지 않는다.

### normal — 표면 법선

이미지마다 같은 해상도의 3채널 16비트 PNG가 필요하다.
채널 순서는 RGB다.
`n = png / 65535 * 2 - 1`로 디코딩한다.
그다음 각 벡터를 다시 정규화한다.
좌표계는 OpenCV 카메라 좌표계다.
+x는 오른쪽, +y는 아래, +z는 장면 안쪽이다.
벡터는 카메라를 향한다.
선택 마스크의 0이 아닌 픽셀은 유효하다.
마스크가 없으면 유한하고 0이 아닌 벡터가 유효하다.
무효 및 패딩 타깃은 내부에서 `(0, 0, 0)`이다.
리사이즈는 성분에 이중 선형 보간을 적용한다.
이후 벡터를 다시 정규화한다.
마스크는 최근접 보간한다.
수평 반전 시 x 성분의 부호도 바꾼다.
YAML의 기본 폴더는 `normals_dir: normals`와 `masks_dir: masks`다.
검증은 평균·중앙값 각도 오차를 도 단위로 보고한다.
11.25도, 22.5도, 30도 이내 비율도 보고한다.

## 이미지 쌍과 기타 작업

### restore — 복원

손상 입력과 깨끗한 RGB 타깃을 쌍으로 둔다.
두 이미지의 해상도는 정확히 같아야 한다.
기본 경로는 `inputs/.../image.jpg`와 `targets/.../image.jpg`다.
검증은 원본 해상도를 유지한다.
배치에 필요한 만큼만 패딩한다.
지표는 원본 이미지 영역에서 계산한다.
학습에서는 쌍에 같은 자르기와 수평 반전을 적용한다.

| YAML 키 | 기본값 | 의미 |
|---|---|---|
| `input_dir` | `inputs` | 손상 입력 폴더 |
| `target_dir` | `targets` | 깨끗한 타깃 폴더 |
| `target_stem_suffix` | 없음 | 타깃 검색용 이름 접미사 |
| `target_stem_suffixes` | 없음 | 접미사 목록 |
| `degradation` | 없음 | `deblur`, `denoise` 같은 메타데이터 |
| `dataset` | 없음 | 데이터셋 또는 출처 이름 |

형식상 `nc: 1`, `names: {0: image}`를 쓴다.
결과는 검출 박스가 아닌 `Results.restored`로 제공한다.

### matte — 알파 매트

RGB 이미지와 같은 이름의 단일 채널 매트를 쓴다.
0은 배경이고 255는 전경이다.
루트 폴더에는 `images/`와 매트 폴더를 둔다.
매트 폴더는 `mattes`, `matte`, `gt`, `masks`, `mask`, `alpha` 중에서 자동 탐지한다.
또는 YAML에 `path`, `val_images`, `val_mattes`를 지정한다.
`train_images`, `train_mattes`는 선택 사항이다.
경로는 `path` 기준 상대 경로 또는 절대 경로다.
매트는 `0..1`의 불투명도로 읽는다.
크기가 다르면 이중 선형 보간으로 맞춘다.
원본 이미지 영역에서 MAE와 S-measure를 계산한다.
최적 체크포인트 기준은 S-measure다.
형식상 `nc: 1`, `names: {0: matte}`를 쓴다.
결과는 `Results.matte`로 제공한다.
제공 자료의 버전에서는 추론 기반 검증만 지원한다.

### ocr — 문자 인식

분할마다 JSONL 파일 하나를 쓴다.
이미지 하나에 JSON 객체 한 줄을 쓴다.

```json
{"image":"receipt.jpg","regions":[{"polygon":[[10,12],[118,14],[117,40],[9,38]],"text":"TOTAL 12.50"}]}
```

다각형은 절대 픽셀 좌표의 네 점이다.
순서는 왼쪽 위, 오른쪽 위, 오른쪽 아래, 왼쪽 아래다.
읽을 수 없는 글자는 `text: "###"`로 표시한다.
해당 영역은 인식 점수에서 제외한다.
겹치는 예측도 검출 매칭에서 벌점 처리하지 않는다.
루트에 `images/<split>/`과 `labels/<split>.jsonl`을 둘 수 있다.
또는 YAML에 `path`와 선택 `images`, `labels` 폴더를 쓴다.
형식상 `nc: 1`, `names: {0: text}`를 쓴다.
결과는 `Results.ocr`로 제공한다.
제공 자료의 버전에서는 추론 기반 검증만 지원한다.

검출 hmean은 IoU 0.5 초과로 일대일 매칭한다.
종단 간 F1은 매칭과 텍스트 일치를 모두 요구한다.
텍스트는 NFKC 정규화와 공백 제거 후 비교한다.
대소문자는 구분한다.
매칭된 쌍의 1-NED도 보고한다.
최적 체크포인트 기준은 종단 간 F1이다.

### classify — 이미지 분류

클래스별 이미지 폴더를 쓴다.

```text
dataset_root/
  train/class_a/*.jpg
  train/class_b/*.jpg
  val/class_a/*.jpg
  val/class_b/*.jpg
```

학습에는 `train/`이 필요하다.
클래스 ID는 학습 폴더 이름 정렬 순서로 정한다.
검증에는 `val/`이 필요하다.
다른 분할은 학습 또는 체크포인트와 같은 클래스 폴더를 써야 한다.
`test/`는 선택 사항이다.
기본 학습과 검증 명령은 `test/`를 사용하지 않는다.
지원 확장자는 `classify_dataset.IMAGE_EXTENSIONS`를 따른다.

### gaze, point, 이벤트 히스토그램, 로봇 정책, albedo

- `gaze`: 학습·검증용 데이터 파일 규격이 구현되지 않았다.
- `point`: 모델 출력 작업이다. 전용 텍스트 라벨 형식은 없다. 모델이 박스 중심을 내부에서 유도할 수 있다.
- 이벤트 히스토그램: YOLO9과 RF-DETR 검출에 `.npy` HWC 배열을 쓴다. 양극성, 음극성 순서로 유한한 음이 아닌 카운트 평면 2개를 둔다. `input_profile`에 `format: event_histogram`, `layout: HWC`, `polarity: positive_negative`, `encoding: counts`, 양수 scale과 양의 정수 `window_us`를 지정한다. 라벨은 일반 검출 TXT다.
- 로봇 정책 `act`: LeRobot v3 데이터셋 폴더나 Hub ID를 쓴다. 에피소드, 카메라, 상태, 행동 특성이 필요하다. 검출 YAML은 쓰지 않는다.
- `albedo`: 이미지와 같은 이름의 `.npy`를 `albedo/<split>/`에 둔다. 타깃은 이미지와 같은 크기의 `(H, W, 3)` 선형 RGB 실수다. 값은 유한한 `0..1` 범위다. 필요하면 `input_dir`과 `albedo_dir`을 단일 폴더 이름으로 지정한다. 표시용 PNG와 sRGB 값은 정량 타깃이 아니다.
