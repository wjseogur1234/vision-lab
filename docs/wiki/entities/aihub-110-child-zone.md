---
type: entity
tags: [dataset, aihub, cctv, bbox, video]
sources: []
created: 2026-11-16
updated: 2026-11-20
---

# AI Hub 110 — 어린이 보호구역 내 어린이 도로보행 위험행동 영상 데이터

CCTV로 찍은 위험행동 영상이다. 프레임마다 사람 상자가 있다.
첫 과제의 보행자 검출에 쓴다.

> [!note] 근거
> 2026-11-20에 `data/raw/`의 파일을 확인했다.

## 1. 위치와 용량

접근 경로는 `data/raw/110.어린이_보호구역_내_어린이_도로보행_위험행동_영상_데이터/01.데이터/`다.
디스크 사용량은 399 GiB다(`du -shL` 기준).

- `1.Training`만 있다. `2.Validation`은 없다.
- CCTV 분류(`1.CCTV`)만 받았다.

## 2. 폴더 구조와 파일 수

`1.Training/` 아래에 라벨과 원천 폴더가 있다.
각 묶음은 `1.CCTV/` 또는 `1.cctv/`를 쓴다.
원천 폴더에는 이미지와 clip이 있다.

| 묶음 | XML | JPG | MP4 |
|---|---:|---:|---:|
| 기본 | 57,602 | 47,400 | 264 |
| `0708_add` | 9,600 | 4,200 | 61 |
| `0915_add` | 63,371 | 63,301 | 479 |
| 합계 | 130,573 | 114,901 | 804 |

추가분 `0915_add` 라벨 폴더에 `.lnk` 35개가 있다.

## 3. 파일 대응

- XML과 JPG는 행동 묶음과 영상 이름 아래에 있다.
- MP4는 `clip/` 아래의 행동 묶음에 있다.
- 대응을 찾을 때 이름의 대소문자 차이를 확인한다.
- 프레임별 대응 수는 추가 확인이 필요하다.

## 4. 이전 조사 기록

2026-11-16 조사에서는 아래 대응 후보를 찾았다.

- `driveway_walk`의 라벨과 이미지가 있었다.
- `fall_down`은 1, 2 묶음에서 둘 다 있었다.
- 당시 ZIP 안의 XML은 130,201개였다.
- 현재 경로의 XML은 130,573개다.
- 두 집계의 차이는 확인하지 않았다.

## 5. 라벨 XML 형식

Pascal VOC 형식이다. 프레임마다 XML 1개다.

```xml
<annotation>
  <size><width>3840</width><height>2160</height><depth>3</depth></size>
  <object>
    <name>person</name>
    <bndbox><xmin>3131</xmin><ymin>1182</ymin><xmax>3341</xmax><ymax>1640</ymax></bndbox>
  </object>
  <object>
    <name>vehicle</name>
    <bndbox><xmin>0</xmin><ymin>692</ymin><xmax>274</xmax><ymax>1080</ymax></bndbox>
  </object>
</annotation>
```

- 이미지 크기가 라벨에 있다. 확인한 파일은 3840×2160이다.
- 확인한 클래스 이름은 `person`, `vehicle`, `license plate`다. 파일 1개에서 본 것이다. 전체 클래스 목록은 세지 않았다.
- XML의 `<filename>`은 믿을 수 없다. 실제 이름과 다른 값(`..._crosswalking_..._00001.txt`)이 들어 있다. 실제 경로와 파일 이름으로 짝을 맞춘다.

## 6. 이 프로젝트에서의 쓰임

- 이미지와 라벨의 대응을 확인한 프레임을 쓴다.
- 보조 학습과 별도 평가에 쓴다. ([분할 계획 6절](../analyses/dataset-split-plan.md#6-ai-hub-110-사용-계획))
- [aihub-101-cctv](aihub-101-cctv.md)와 다른 점: 영상에서 연속으로 뽑은 프레임이라 서로 매우 비슷하다. 쓸 때는 프레임을 건너뛰어 뽑는다.

관련 데이터셋: [aihub-101-cctv](aihub-101-cctv.md), [aihub-095-accident](aihub-095-accident.md)
