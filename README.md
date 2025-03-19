# HR 관리 시스템

HR 관리 시스템은 인사 관리 업무를 효율적으로 처리할 수 있도록 도와주는 종합 솔루션입니다. 연차휴가 계산, 근로계약서 작성, 임금대장 관리, 임금명세서 생성 등 다양한 기능을 제공합니다.

## 주요 기능

### 🗓️ 연차휴가 계산기
- 입사일 기준 연차휴가 계산
- 회계연도 기준 연차휴가 계산
- 연차휴가 발생 테이블 생성 및 시각화

### 📝 근로계약서
- 근로계약서 템플릿 제공
- 맞춤형 근로계약서 작성
- PDF 형식으로 다운로드

### 💰 임금대장
- 직원 정보 관리
- 임금 지급 기록 관리
- 월별/연간 보고서 생성

### 💵 임금명세서
- 개별 임금명세서 생성
- 일괄 임금명세서 생성
- PDF 형식으로 다운로드

## 설치 방법

### 요구 사항
- Python 3.8 이상
- pip (Python 패키지 관리자)

### 설치 단계

1. 저장소 클론
```bash
git clone https://github.com/yourusername/hr-management-system.git
cd hr-management-system
```

2. 가상 환경 생성 및 활성화 (선택 사항)
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

## 사용 방법

1. 애플리케이션 실행
```bash
streamlit run app.py
```

2. 웹 브라우저에서 애플리케이션 접속
```
http://localhost:8501
```

## 프로젝트 구조

```
hr_management_system/
├── app.py                      # 메인 애플리케이션
├── requirements.txt            # 필요한 패키지 목록
├── README.md                   # 프로젝트 설명
├── LICENSE                     # 라이센스 파일
├── annual_leave/               # 연차휴가 계산기 모듈
│   ├── annual_leave_calculator.py
│   └── annual_leave_ui.py
├── employment_contract/        # 근로계약서 모듈
│   └── employment_contract.py
├── payroll_ledger/             # 임금대장 모듈
│   └── payroll_ledger.py
├── pay_statement/              # 임금명세서 모듈
│   └── pay_statement.py
├── utils/                      # 유틸리티 함수
├── data/                       # 데이터 저장 디렉토리
└── static/                     # 정적 파일 (CSS, 이미지 등)
    ├── css/
    ├── fonts/
    └── images/
```

## 기능 상세 설명

### 연차휴가 계산기

연차휴가 계산기는 한국 근로기준법에 따라 직원의 연차휴가를 계산합니다.

- **입사일 기준 계산**: 직원의 입사일을 기준으로 연차휴가를 계산합니다.
  - 1년 미만 근무: 1개월 개근 시 1일의 유급휴가 발생 (최대 11일)
  - 1년 이상 근무: 15일의 유급휴가 발생
  - 3년 이상 근무: 2년마다 1일씩 추가 발생 (최대 25일)

- **회계연도 기준 계산**: 회사의 회계연도를 기준으로 연차휴가를 계산합니다.

- **연차휴가 발생 테이블**: 향후 5년간의 연차휴가 발생 추이를 테이블과 그래프로 확인할 수 있습니다.

### 근로계약서

근로계약서 모듈은 한국 근로기준법에 맞는 근로계약서 템플릿을 제공합니다.

- **기본 템플릿**: 근로계약서 기본 템플릿을 제공합니다.
- **맞춤형 작성**: 사업주 정보, 근로자 정보, 근로 조건 등을 입력하여 맞춤형 근로계약서를 작성할 수 있습니다.
- **PDF 생성**: 작성한 근로계약서를 PDF 형식으로 다운로드할 수 있습니다.

### 임금대장

임금대장 모듈은 직원 정보와 임금 지급 기록을 관리합니다.

- **직원 관리**: 직원 정보를 추가, 수정, 삭제할 수 있습니다.
- **임금 지급 관리**: 임금 지급 기록을 추가, 수정, 삭제할 수 있습니다.
- **보고서 생성**: 월별/연간 임금 지급 보고서를 생성하고 엑셀 파일로 다운로드할 수 있습니다.

### 임금명세서

임금명세서 모듈은 임금대장 데이터를 기반으로 임금명세서를 생성합니다.

- **개별 임금명세서**: 특정 직원의 특정 지급일에 대한 임금명세서를 생성합니다.
- **일괄 임금명세서**: 특정 월의 모든 직원에 대한 임금명세서를 일괄 생성합니다.
- **PDF 생성**: 생성한 임금명세서를 PDF 형식으로 다운로드할 수 있습니다.

## 기여 방법

1. 이 저장소를 포크합니다.
2. 새 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`).
3. 변경 사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`).
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`).
5. Pull Request를 생성합니다.

## 라이센스

이 프로젝트는 MIT 라이센스에 따라 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 연락처

프로젝트 관리자 - [@yourusername](https://github.com/yourusername)

프로젝트 링크: [https://github.com/yourusername/hr-management-system](https://github.com/yourusername/hr-management-system)
