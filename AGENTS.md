# AGENTS.md

## git commit / push 할 때

- 커밋 또는 푸시하기 전에 항상 커밋 메시지와 대상 파일을 사용자에게 보여주고 검토를 받은 뒤 진행한다.
- 커밋 메시지는 [Conventional Commits](https://www.conventionalcommits.org/) 형식을 따른다.
  - 형식: `<type>(<scope>): <description>` (scope는 생략 가능)
  - 주요 type: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`
  - Breaking change는 type 뒤에 `!`를 붙이거나 footer에 `BREAKING CHANGE:`를 적는다.
  - 예: `docs: add glossary for residual pedestrian terms`
