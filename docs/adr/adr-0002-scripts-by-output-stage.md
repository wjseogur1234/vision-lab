---
type: adr
status: 승인
superseded_by:
tags: [code-structure, scripts, hydra, preprocessing]
sources: ["wiki/phase_0/analyses/dataset-split-plan.md", "wiki/phase_0/analyses/raw-manifest.md"]
created: 2026-11-26
updated: 2026-11-26
---

# ADR-0002 실행 스크립트는 산출물 단계로 나눈다

## 상태

승인 (2026-11-25). 커밋 `b7b365d`로 반영했다.

## 맥락

- Phase 0 코드는 `src/data/` 모듈마다 `main()`이 있었다. 라이브러리 함수가 Hydra 설정 객체(`args`)를 받았다.
- 전처리 산출물은 세 단계다. 단계마다 위치와 쓰임이 다르다.
  - raw manifest: `data/interim/`. 원본 전체를 읽어 느리다. 지워도 된다.
  - 분할 안: `configs/data/*.splits.yaml`. 사람이 검토한 뒤 git에 올린다.
  - COCO 데이터셋: `data/processed/`. 버전별로 여러 번 만든다.
- 한 프로세스에서 `@hydra.main` 함수를 연달아 부르면 `GlobalHydra is already initialized` 오류가 난다.

## 선택지

| 선택지 | 장점 | 단점 |
|---|---|---|
| A. 모듈마다 스크립트 1개 | 옮기기 쉽다 | 모듈 경계가 실행 단위를 정한다. 단계 기준이 아니다 |
| B. 전체 파이프라인 스크립트 1개 | 명령이 하나다 | 분할 안 검토를 건너뛴다. 느린 1단계를 매번 다시 돈다 |
| C. 산출물 단계마다 스크립트 1개 | 단계 사이에 검토와 재사용이 된다 | 명령을 세 번 실행한다 |

## 결정

- 선택지 C를 쓴다. `scripts/build_raw_manifest.py`, `scripts/propose_splits.py`, `scripts/build_coco.py`.
- Hydra와 OmegaConf는 `scripts/`에서만 쓴다. `src/data/` 함수는 값을 인자로 받는다.
- 세 단계를 묶는 스크립트는 만들지 않는다.

## 결과

- 얻는 것: `src/data/` 함수를 Hydra 없이 부를 수 있다. 테스트와 노트북에서 바로 쓴다.
- 얻는 것: 함수 사이 숨은 의존이 없다. 값은 인자와 반환값으로만 오간다.
- 잃는 것: 실행 방법이 `python -m data.X`에서 `python scripts/X.py`로 바뀌었다.
- 지킬 것: 단계를 묶어야 하면 새 스크립트가 라이브러리 함수를 직접 부른다. 다른 스크립트의 `main()`을 부르지 않는다.

## 관련

- [raw-manifest](../wiki/phase_0/analyses/raw-manifest.md)
- [dataset-split-plan](../wiki/phase_0/analyses/dataset-split-plan.md) 4절, 5절
