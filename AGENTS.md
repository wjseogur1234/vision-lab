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
