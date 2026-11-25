---
type: adr
status: 승인
superseded_by:
tags: [dataset, label-format, coco, libreyolo]
sources: ["wiki/phase_0/analyses/dataset-split-plan.md", "wiki/phase_0/concepts/libreyolo-dataset-formats.md"]
created: 2026-11-26
updated: 2026-11-26
---

# ADR-0001 라벨 형식은 COCO JSON

## 상태

승인 (2026-11-21). 사용자 결정이다. ADR은 2026-11-26에 기록했다.

## 맥락

- LibreYOLO는 YOLO TXT와 COCO JSON을 모두 읽는다.
- YOLO 계열 예제는 대부분 YOLO TXT를 쓴다.
- YOLO TXT는 이미지 옆 `labels/` 폴더에 라벨을 둔다.
- 원본 이미지(`RAW_DATA_DIR`)는 읽기 전용으로 마운트한다.
- 101 Bbox raw manifest는 163,917행이다. 복사하면 용량과 시간이 많이 든다.

## 선택지

| 선택지 | 장점 | 단점 |
|---|---|---|
| A. YOLO TXT + 이미지 복사 | 예제와 같다. 도구가 많다 | 이미지를 복사해야 한다. 용량과 시간이 든다 |
| B. YOLO TXT + 이미지 심볼릭 링크 | 복사하지 않는다 | 이미지 수만큼 링크를 관리한다. `labels/` 위치 규칙이 링크 구조에 묶인다 |
| C. COCO JSON | 원본 경로를 `file_name`에 적는다. 복사와 링크가 없다 | YOLO TXT 전용 도구는 바로 쓸 수 없다 |

## 결정

- 선택지 C를 쓴다. 분할마다 COCO JSON 1개를 만든다.
- `file_name`은 `data/raw/` 기준 원본 경로다. 이미지는 복사하지 않는다.

## 결과

- 얻는 것: 데이터셋 버전을 늘려도 이미지 용량이 늘지 않는다. 생성은 수 초면 끝난다.
- 잃는 것: 학습할 때 이미지를 HDD 원본에서 읽는다. 느리면 SSD로 복사하고 YAML 루트만 바꾼다.
- 잃는 것: `--cache disk`를 쓸 수 없다. 원본 옆에 캐시를 쓰지 못한다.
- 지킬 것: `data/raw/` 링크 경로가 바뀌면 모든 데이터셋 YAML의 루트도 바꾼다.

## 관련

- [dataset-split-plan](../wiki/phase_0/analyses/dataset-split-plan.md) 5.3절, 5.4절
- [libreyolo-dataset-formats](../wiki/phase_0/concepts/libreyolo-dataset-formats.md)
