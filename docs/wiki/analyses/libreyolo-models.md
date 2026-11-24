---
type: analysis
tags: [libreyolo, object-detection]
sources: ["wiki/sources/libreyolo-model-reference.md"]
created: 2026-11-19
updated: 2026-11-24
---

# LibreYOLO 모델

이 프로젝트의 첫 과제는 CCTV 보행자 검출이다.
학습에는 [aihub-101-cctv](../entities/aihub-101-cctv.md) 데이터를 쓴다.

## 프로젝트 환경

- `train` 그룹은 `libreyolo==1.8.0`를 지정한다. [pyproject.toml](../../../pyproject.toml)
- 확인일 기준 PyPI 최신 버전은 1.8.0이다. [libreyolo-model-reference](../sources/libreyolo-model-reference.md)
- 의존성은 프로젝트의 `uv.lock`에 잠겨 있다.
- Docker의 `lab` 서비스에서 학습 환경을 실행한다.
- `lab`은 호스트와 같은 UID(기본 1000)의 `lab` 계정으로 실행한다. 결과 파일이 root 소유가 되지 않는다.
- 가중치는 프로젝트 루트의 `weights/`에 내려받는다.
- YOLOX-s(`yolox-s`)로 COCO JSON 학습 1 epoch를 확인했다(2026-11-24). 결과는 [분할 계획 8.2절](dataset-split-plan.md#82-학습-확인)에 있다.
- 다른 모델의 로딩과 학습은 실행하지 않았다.
- 실험 기록 도구 연동은 [libreyolo-mlflow](libreyolo-mlflow.md)에 있다.

## 보행자 박스 검출 후보

공식 문서의 1.8.0 지원 범위를 기준으로 정리했다. [libreyolo-model-reference](../sources/libreyolo-model-reference.md)

| 용도 | 모델 계열 |
|---|---|
| 기본 설치 학습 예제 | YOLOv9 |
| 추가 의존성이 있는 후보 | RF-DETR |
| 다른 검출 후보 | YOLOX, YOLOv7, YOLO-NAS, RTMDet, PicoDet, DEIM, D-FINE, EdgeCrafter, RT-DETR |
| 추론 전용 예시 | DETR, Faster R-CNN, RetinaNet, SSD, FCOS, CenterNet |

YOLOv9 학습 예제의 모델 ID는 `yolo9-t`다.
가중치 파일명은 `LibreYOLO9t.pt`다.
RF-DETR은 설치 시 `rfdetr` 옵션을 확인한다.
다른 후보는 모델별 학습 지원과 의존성을 확인한다. [libreyolo-model-reference](../sources/libreyolo-model-reference.md)

## 모델별 검출 데이터 형식

이 표는 위 보행자 박스 검출 후보를 다룬다.
LibreYOLO 1.8.0 공식 문서를 기준으로 정리했다.
모델별 학습 예제와 공통 검출 형식을 대조했다.
표의 형식은 검출 작업에만 적용한다.
실제 학습은 YOLOX만 확인했다.
[공통 데이터 형식](https://www.libreyolo.com/docs/reference/dataset-formats)
작업별 규격은 [LibreYOLO 데이터셋 형식](../concepts/libreyolo-dataset-formats.md)을 참고한다.

| 모델 계열 | 검출 학습 데이터 형식 | 모델 문서 |
|---|---|---|
| YOLOv9 | YOLO TXT 또는 COCO JSON + YAML | [YOLOv9](https://www.libreyolo.com/docs/models/yolov9) |
| RF-DETR | YOLO TXT 또는 COCO JSON + YAML | [RF-DETR](https://www.libreyolo.com/docs/models/rf-detr) |
| YOLOX | YOLO TXT 또는 COCO JSON + YAML | [YOLOX](https://www.libreyolo.com/docs/models/yolox) |
| YOLOv7 | YOLO TXT 또는 COCO JSON + YAML | [YOLOv7](https://www.libreyolo.com/docs/models/yolov7) |
| YOLO-NAS | YOLO TXT 또는 COCO JSON + YAML | [YOLO-NAS](https://www.libreyolo.com/docs/models/yolo-nas) |
| RTMDet | YOLO TXT 또는 COCO JSON + YAML | [RTMDet](https://www.libreyolo.com/docs/models/rtmdet) |
| PicoDet | YOLO TXT 또는 COCO JSON + YAML | [PicoDet](https://www.libreyolo.com/docs/models/picodet) |
| DEIM | YOLO TXT 또는 COCO JSON + YAML | [DEIM](https://www.libreyolo.com/docs/models/deim) |
| D-FINE | YOLO TXT 또는 COCO JSON + YAML | [D-FINE](https://www.libreyolo.com/docs/models/d-fine) |
| EdgeCrafter | YOLO TXT 또는 COCO JSON + YAML | [EdgeCrafter](https://www.libreyolo.com/docs/models/edgecrafter) |
| RT-DETR | YOLO TXT 또는 COCO JSON + YAML | [RT-DETR](https://www.libreyolo.com/docs/models/rt-detr) |
| DETR, Faster R-CNN, RetinaNet, SSD, FCOS, CenterNet | 학습 형식 해당 없음. LibreYOLO에서 추론 전용 | [모델 목록](https://www.libreyolo.com/docs/models) |

검출 TXT는 이미지마다 라벨 파일 하나를 쓴다.
각 줄은 `class_id cx cy width height` 순서다.
좌표와 크기는 원본 이미지 기준으로 0~1로 정규화한다.
YAML에는 데이터 경로, 분할, 클래스 이름을 적는다.
COCO JSON을 쓸 때는 YAML에 `annotations`를 지정한다.
[데이터셋 학습 문서](https://www.libreyolo.com/docs/train/datasets)

> [!warning] 작업별 라벨 차이
> 검출 박스는 자세의 관절점 정보를 담지 않는다.
> 분할에 필요한 실제 윤곽 정보도 담지 않는다.
> 분할, 자세, 회전 박스 학습은 작업별 형식을 확인한다.
> RF-DETR과 EdgeCrafter는 여러 작업을 지원한다.
> 같은 계열이라도 가중치와 작업을 함께 확인한다.
> [데이터 형식](https://www.libreyolo.com/docs/reference/dataset-formats), [RF-DETR](https://www.libreyolo.com/docs/models/rf-detr), [EdgeCrafter](https://www.libreyolo.com/docs/models/edgecrafter)

## 설치 버전 확인

프로젝트 루트에서 학습 컨테이너의 패키지 버전을 조회한다.

```sh
docker compose run --rm lab python -c 'from importlib.metadata import version; print(version("libreyolo"))'
```
