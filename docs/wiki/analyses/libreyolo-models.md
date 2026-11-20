---
type: analysis
tags: [libreyolo, object-detection]
sources: ["[[libreyolo-model-reference]]"]
created: 2026-11-19
updated: 2026-11-19
---

# LibreYOLO 모델

이 프로젝트의 첫 과제는 CCTV 보행자 검출이다.
학습에는 [aihub-101-cctv](../entities/aihub-101-cctv.md) 데이터를 쓴다.

## 프로젝트 환경

- `train` 그룹은 `libreyolo==1.8.0`를 지정한다. [pyproject.toml](../../../pyproject.toml)
- 확인일 기준 PyPI 최신 버전은 1.8.0이다. [libreyolo-model-reference](../sources/libreyolo-model-reference.md)
- 작업 폴더에서 모델 가중치와 버전 잠금 파일을 찾지 못했다.
- 호스트의 Python 3에서 LibreYOLO를 찾지 못했다.
- Docker 소켓 권한이 없어 학습 컨테이너를 확인하지 못했다.
- 모델 로딩과 학습은 실행하지 않았다.

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

## 설치 버전 확인

프로젝트 루트에서 학습 컨테이너의 패키지 버전을 조회한다.

```sh
docker compose run --rm train python -c 'from importlib.metadata import version; print(version("libreyolo"))'
```
