# CLAUDE.md — autolife 프로젝트 가이드

이 파일은 Claude Code가 이 레포에서 작업할 때 참고하는 컨텍스트 문서입니다.

## 프로젝트 개요

**autolife**는 이슈/프롬프트를 입력받아 앱을 자동으로 생성하고 PR을 만드는 워크플로 레포입니다.

- **목표**: 이슈 또는 @claude 멘션 → 코드 자동 생성 → PR 자동 등록
- **스택**: 현재 스택 미정 (빈 레포에서 시작). 앱 생성 시 요청에 맞게 스택 선택

> 스택이 확정되면 아래 항목을 업데이트하세요.

## 현재 스택 (초기 상태)

| 항목 | 내용 |
|------|------|
| 언어 | 미정 (요청에 따라 TypeScript / Python 등 선택) |
| 프레임워크 | 미정 |
| 패키지 매니저 | 미정 |
| 테스트 | 미정 |
| CI/CD | GitHub Actions + anthropics/claude-code-action@v1 |

## 폴더 구조

apps/
  <app-name>/   각 앱별 독립 폴더
.claude/
  commands/
    new-app.md  슬래시 커맨드 템플릿
  settings.json Claude Code 권한/도구 설정
.github/
  workflows/
    claude.yml  @claude 트리거 워크플로
CLAUDE.md
README.md

## 코딩 규칙

1. 언어/스타일: 각 앱 요청 시 명시된 언어를 따른다. 미명시 시 TypeScript 기본.
2. 파일 인코딩: UTF-8, LF 줄바꿈
3. 커밋 메시지: <type>(<scope>): <summary> 형식 (예: feat(todo-app): add initial scaffold)
4. 브랜치 이름: app/<app-name> 또는 feat/<feature-name>
5. 테스트: 가능하면 기본 테스트 파일 포함 (smoke test 수준이라도)
6. README: 각 앱 폴더에 최소한의 README.md 포함

## 새 앱/기능 생성 시 따라야 할 절차

Claude가 이슈 또는 @claude 멘션으로 앱 생성 요청을 받으면 아래 순서를 따릅니다:

1. 명세 파악: 이슈/코멘트에서 앱 이름, 기능 요구사항, 선호 스택을 추출
2. 브랜치 생성: app/<app-name> 브랜치를 main에서 분기
3. 스캐폴드: apps/<app-name>/ 디렉터리 생성 및 기본 구조 설정
4. 구현: 요구사항에 맞게 코드 작성
5. 테스트: 기본 테스트 파일 작성 또는 실행
6. 커밋: 의미 단위로 커밋
7. PR 생성: 이슈 번호 연결(Closes #N), 구현 내용 요약 포함

자세한 절차는 .claude/commands/new-app.md 참고.

## 주의사항

- secrets(API 키 등)는 절대 코드에 하드코딩하지 않는다. GitHub Secrets 사용.
- 외부 의존성 추가 시 이유를 PR 설명에 명시한다.
- 자동 생성 코드라도 코드 품질 기준을 지킨다.
