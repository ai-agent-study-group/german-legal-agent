# GitHub에서 문서 작성·수정하기

Markdown 문서는 GitHub 저장소 화면에서 읽고 만들고 수정할 수 있습니다.
문서 협업을 위한 별도 웹사이트 배포는 필요하지 않습니다. 저장소에 파일이 올라가고 참여자에게 필요한 접근 권한이 있어야 합니다.
이 안내를 작성한 것과 실제 저장소 업로드·권한 설정을 완료한 것은 별개입니다.

## 기존 문서 수정

1. GitHub에서 저장소를 열고 수정할 `.md` 파일을 선택합니다.
2. 연필 모양의 편집 버튼으로 내용을 수정합니다.
3. `Preview`에서 표·링크·줄바꿈을 확인합니다.
4. `Commit changes`에서 수정 내용을 설명합니다.
5. 새 브랜치를 만들어 PR을 여는 선택지를 사용합니다. 예: `docs/meeting-2026-10-15`.
6. PR에서 팀원이 내용을 확인하고, 저장소의 리뷰·검사 조건에 맞게 병합합니다.

브랜치는 원본과 별도로 변경을 준비하는 공간이고, PR은 그 변경을 함께 검토하는 요청입니다.
문서 변경에도 기존 [기여 규칙](../CONTRIBUTING.md)의 PR 절차를 적용합니다.

## 새 회의록 만들기

1. [회의록 템플릿](meetings/TEMPLATE.md)을 열고 본문을 복사합니다.
2. 저장소에서 `Add file → Create new file`을 선택합니다.
3. 파일 이름에 `docs/meetings/YYYY-MM-DD.md`를 입력합니다.
4. 본문을 붙여넣고 날짜·안건을 작성합니다. 미정 내용은 빈칸이나 `?`로 둡니다.
5. 미리보기를 확인하고 새 브랜치·PR로 변경을 제안합니다.
6. 같은 브랜치에서 `docs/meetings/README.md`의 목록에도 회의록 링크를 추가합니다.

폴더 경로와 파일 이름을 함께 입력해 새 폴더 안의 파일도 만들 수 있습니다.
여러 파일을 함께 수정할 때는 GitHub의 `github.dev` 웹 편집기를 활용할 수도 있습니다.

## 회의 중·후 기록

- 의견·후보는 논의 메모, 합의한 내용은 결정 사항에 기록합니다.
- 담당자·기한·다음 일정도 합의한 내용만 채웁니다.
- 여러 명이 같은 문서를 편집한다면 회의 기록자를 정하거나 수정할 부분을 나누는 방식을 논의할 수 있습니다.
- 회의 이후 같은 PR에서 기록을 보완하고, 확정된 내용을 프로젝트·역할 문서에 반영할 수 있습니다.

## 저장소 관리자와 확인할 것

| 항목 | 확인 내용 |
| --- | --- |
| 저장소 주소·공개 범위 | ? |
| 참여자 초대·쓰기 권한 | ? |
| 문서 리뷰·병합 담당 | ? |
| 브랜치 보호·필수 검사 | 실제 GitHub 설정은 ? |

쓰기 권한이 없으면 포크와 PR로 제안할 수 있지만, 비공개 저장소는 접근 권한과 포크 정책도 확인해야 합니다.

GitHub Pages는 문서를 별도 정적 사이트로 보여주고 싶을 때 검토할 수 있습니다.
이것과 실제 agent 웹앱·API의 배포 환경 선택은 각각 별도 논의 항목입니다.

## 공식 안내

- [파일 수정](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files)
- [파일 생성](https://docs.github.com/en/repositories/working-with-files/managing-files/creating-new-files)
- [PR 시작하기](https://docs.github.com/en/pull-requests/get-started/pull-request-quickstart)
- [GitHub 웹 편집기](https://docs.github.com/en/codespaces/the-githubdev-web-based-editor)
- [GitHub Pages 소개](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)
