# /new-app — 새 앱 생성 커맨드

Claude Code 슬래시 커맨드: `/new-app`

이 커맨드는 이슈 또는 @claude 멘션에서 앱 생성 요청을 받았을 때 따를 절차를 정의합니다.

---

## 사용법

Claude Code에서 다음과 같이 호출합니다:

    /new-app

또는 GitHub 이슈/코멘트에서:

    @claude /new-app 앱 이름: todo-app, 기능: 할일 CRUD, 스택: TypeScript + Express

---

## 입력 명세 (파싱 대상)

Claude는 이슈 본문 또는 멘션 코멘트에서 아래 항목을 추출합니다:

| 항목 | 필수 | 설명 | 예시 |
|------|------|------|------|
| 앱 이름 | 필수 | 영문 소문자, 하이픈 허용 | `todo-app` |
| 기능 요구사항 | 필수 | 구현할 기능 목록 | "할일 추가/삭제/완료 표시" |
| 스택 | 선택 | 언어/프레임워크 | TypeScript, Python, React 등 |
| 추가 지시사항 | 선택 | 특수 요구사항 | "REST API만, DB 없이" |

스택이 명시되지 않으면 TypeScript를 기본으로 사용합니다.

---

## 실행 절차

### 1단계: 명세 파악

이슈/코멘트 내용에서 다음을 추출합니다:
- APP_NAME: 앱 이름 (영문 소문자 + 하이픈)
- FEATURES: 기능 목록
- STACK: 사용 스택
- ISSUE_NUMBER: 트리거된 이슈 번호

불명확한 항목이 있으면 코멘트로 질문합니다.

### 2단계: 브랜치 생성

    git checkout main
    git pull origin main
    git checkout -b app/{APP_NAME}

### 3단계: 스캐폴드 생성

`apps/{APP_NAME}/` 디렉터리를 생성하고 기본 구조를 설정합니다.

TypeScript 기본 구조 예시:

    apps/{APP_NAME}/
    ├── src/
    │   └── index.ts
    ├── tests/
    │   └── index.test.ts
    ├── package.json
    ├── tsconfig.json
    └── README.md

Python 기본 구조 예시:

    apps/{APP_NAME}/
    ├── src/
    │   └── main.py
    ├── tests/
    │   └── test_main.py
    ├── requirements.txt
    └── README.md

### 4단계: 구현

요구사항에 맞게 코드를 작성합니다:
- 기능별로 파일을 분리
- 외부 의존성은 package.json / requirements.txt에 명시
- 환경변수/시크릿은 .env.example로 문서화 (실제 값 커밋 금지)
- 코드에 간단한 JSDoc/docstring 주석 포함

### 5단계: 테스트

최소한의 smoke test를 작성하고 실행합니다:

TypeScript:

    npm install
    npm test

Python:

    pip install -r requirements.txt
    pytest

테스트가 실패하면 수정 후 다시 실행합니다.

### 6단계: 커밋

의미 단위로 커밋합니다:

    git add apps/{APP_NAME}/
    git commit -m "feat({APP_NAME}): add initial scaffold"
    git commit -m "feat({APP_NAME}): implement {FEATURE}"
    git commit -m "test({APP_NAME}): add smoke tests"

### 7단계: PR 생성

다음 형식으로 PR을 생성합니다:

**PR 제목:**

    feat: add {APP_NAME} app

**PR 본문 템플릿:**

    ## 개요

    이슈 #{ISSUE_NUMBER} 에서 요청된 {APP_NAME} 앱을 구현합니다.

    Closes #{ISSUE_NUMBER}

    ## 구현 내용

    - [ ] {FEATURE_1}
    - [ ] {FEATURE_2}
    - [ ] 기본 테스트 추가

    ## 스택

    - 언어/프레임워크: {STACK}

    ## 실행 방법

    {실행 방법 설명}

    ## 주의사항 / 한계

    {있다면 명시}

---

## 체크리스트 (완료 기준)

- [ ] apps/{APP_NAME}/ 디렉터리 생성됨
- [ ] 요구사항의 핵심 기능 구현됨
- [ ] 기본 테스트 통과
- [ ] README.md 포함
- [ ] .env.example 포함 (환경변수 있는 경우)
- [ ] PR 생성 완료 및 이슈 연결됨
