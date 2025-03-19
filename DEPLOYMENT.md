# HR 관리 시스템 배포 가이드

이 문서는 HR 관리 시스템을 깃허브에 올리고 스트림릿으로 공유하는 방법을 설명합니다.

## 1. 깃허브 저장소 생성 및 코드 업로드

1. 깃허브 계정에 로그인합니다.
2. 새 저장소(repository)를 생성합니다:
   - 저장소 이름: `hr-management-system`
   - 설명: `연차휴가 계산기, 근로계약서, 임금대장, 임금명세서 관리 시스템`
   - 공개/비공개 설정: 선택에 따라 결정
   - README 파일 초기화: 체크
   - .gitignore 추가: Python 선택
   - 라이센스: MIT 선택

3. 로컬 저장소 초기화 및 코드 업로드:
```bash
# 현재 디렉토리에서 git 초기화
git init

# 원격 저장소 추가
git remote add origin https://github.com/yourusername/hr-management-system.git

# 모든 파일 추가
git add .

# 커밋 메시지 작성
git commit -m "Initial commit: HR Management System"

# 원격 저장소에 푸시
git push -u origin main
```

## 2. 스트림릿 클라우드 배포

### 스트림릿 클라우드 계정 생성
1. [Streamlit Cloud](https://streamlit.io/cloud)에 접속합니다.
2. 깃허브 계정으로 로그인합니다.

### 앱 배포
1. "New app" 버튼을 클릭합니다.
2. 저장소, 브랜치, 파일 경로를 입력합니다:
   - 저장소: `yourusername/hr-management-system`
   - 브랜치: `main`
   - 파일 경로: `app.py`
3. "Deploy" 버튼을 클릭합니다.
4. 배포가 완료되면 제공된 URL을 통해 앱에 접근할 수 있습니다.

### 앱 설정 (선택사항)
1. 앱 설정에서 앱 이름, 테마, 시간대 등을 설정할 수 있습니다.
2. 비공개 앱으로 설정하려면 "Advanced settings"에서 "Private app" 옵션을 선택합니다.

## 3. 로컬 환경에서 실행

로컬 환경에서 앱을 실행하려면 다음 명령어를 사용합니다:

```bash
# 필요한 패키지 설치
pip install -r requirements.txt

# 앱 실행
streamlit run app.py
```

## 4. 데이터 관리

- 모든 데이터는 `data` 디렉토리에 저장됩니다.
- 중요한 데이터는 정기적으로 백업하는 것이 좋습니다.
- 실제 운영 환경에서는 보안을 위해 데이터베이스 사용을 고려하세요.

## 5. 문제 해결

- 앱 실행 중 오류가 발생하면 콘솔 로그를 확인하세요.
- 깃허브 이슈를 통해 문제를 보고하거나 기능 요청을 할 수 있습니다.
- 코드 기여는 풀 리퀘스트를 통해 가능합니다.

## 6. 추가 리소스

- [Streamlit 문서](https://docs.streamlit.io/)
- [GitHub 문서](https://docs.github.com/)
- [Python 문서](https://docs.python.org/)
