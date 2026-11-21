# AGENTS.md

## git commit / push 할 때

- 커밋 또는 푸시하기 전에 항상 커밋 메시지와 대상 파일을 사용자에게 보여주고 검토를 받은 뒤 진행한다.
- 커밋 메시지는 [Conventional Commits](https://www.conventionalcommits.org/) 형식을 따른다.
  - 형식: `<type>(<scope>): <description>` (scope는 생략 가능)
  - 주요 type: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`
  - Breaking change는 type 뒤에 `!`를 붙이거나 footer에 `BREAKING CHANGE:`를 적는다.
  - 예: `docs: add glossary for residual pedestrian terms`

## 글쓰기 규칙

비행기 정비 매뉴얼 문체(ASD-STE100 Simplified Technical English)에 80% 정도만 맞춰서 한국어로 쓴다.

- 한 문장에 한 가지 생각만 쓴다.
- 문장은 짧게 쓴다. 한 문장은 40자 안쪽으로 쓴다.
- 꾸밈말, 감탄, 빈 인사말과 맺음말은 뺀다.
- 같은 대상은 끝까지 같은 단어로 부른다.
- 숫자, 날짜, 조건, 예외는 빠짐없이 그대로 둔다.
- 해야 할 일은 동사로 분명하게 쓴다.
- 읽기 어색할 만큼 딱딱해지면 조금 풀어도 된다.

## 작업별 Docker 서비스

프로젝트 루트에서 실행한다.

| 작업 | 서비스 | 실행 명령 |
|---|---|---|
| 원본 점검, 데이터 분할, 라벨 변환 | `prep` | `docker compose run --rm prep` |
| 모델 학습, 추론, 평가, CUDA 확인 | `train` | `docker compose run --rm train` |

- `prep`에서 `data/raw/`를 읽고 `data/processed/`에 결과를 쓴다.
- 중간 파일은 `data/interim/`에 쓴다. 이 폴더는 지워도 된다.
- HDD 중간 파일은 `data/interim/HDD/project_261121`에 쓴다.
- `.env`의 `RAW_DATA_DIR`은 `prep`에 읽기 전용으로 연결된다.
- `train`은 `data/processed/`를 읽기 전용으로 읽는다.
- 모델 작업에 필요한 NVIDIA GPU는 `train`에 할당된다.

이미지를 다시 빌드하려면 명령에 `--build`를 추가한다.
`run --rm`의 셸에서 `exit`를 실행하면 컨테이너가 삭제된다.

컨테이너를 유지하려면 다음 명령을 쓴다.

```bash
docker compose up -d train
docker compose exec train bash
docker compose stop train
```

전처리 환경은 `train` 대신 `prep`을 쓴다.
`exec` 셸에서 `exit`를 실행해도 컨테이너는 유지된다.
프로젝트 폴더 밖의 파일은 컨테이너 삭제 시 사라질 수 있다.
