import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT
import os
import datetime
import io
import base64
import requests

def download_korean_font():
    """한글 폰트를 다운로드하고 등록하는 함수"""
    # 폴더 만들기
    font_folder = "my_special_fonts"
    os.makedirs(font_folder, exist_ok=True)

    # 폰트 파일 이름 정하기
    font_file_path = os.path.join(font_folder, "my_korean_font.ttf")

    # 폰트 다운로드할 주소들
    font_download_links = [
        "https://github.com/naver/nanumfont/raw/master/NanumFont/NanumGothic.ttf",
        "https://raw.githubusercontent.com/naver/nanumfont/master/NanumFont/NanumGothic.ttf"
    ]

    # 폰트 다운로드 시도하기
    for link in font_download_links:
        try:
            # 인터넷에서 폰트 파일 가져오기
            response = requests.get(link, timeout=10)
            
            # 폰트 파일 잘 받아왔나 확인하기
            if response.status_code == 200:
                # 폰트 파일 저장하기
                with open(font_file_path, "wb") as font_file:
                    font_file.write(response.content)
                
                # PDF에 폰트 등록하기
                pdfmetrics.registerFont(TTFont('MyKoreanFont', font_file_path))
                
                # 성공했다고 알려주기
                st.success("한글 폰트를 성공적으로 다운로드했어요! 🎉")
                return 'MyKoreanFont'
        
        except Exception as error:
            # 혹시 문제가 생기면 알려주기
            st.warning(f"폰트 다운로드에 문제가 생겼어요: {error}")

    # 만약 모든 시도가 실패하면
    st.error("죄송해요. 폰트를 다운로드할 수 없었어요. 😢")
    return 'Helvetica'  # 기본 폰트 사용

def render_employment_contract_form():
    """
    근로계약서 입력 폼 렌더링 함수
    """
    st.title("📝 근로계약서 생성기")
    
    # 근로계약서 인스턴스 생성
    contract = EmploymentContract()
    
    # 기본 템플릿 데이터 가져오기
    if 'contract_data' not in st.session_state:
        st.session_state.contract_data = contract.get_contract_template()
    
    # 폼 데이터를 위한 임시 변수
    form_data = {}
    for key in st.session_state.contract_data:
        form_data[key] = st.session_state.contract_data[key]
    
    # 폼 생성 - st.form 대신 HTML 폼 사용
    st.subheader("사업주 정보")
    col1, col2 = st.columns(2)
    with col1:
        form_data["company_name"] = st.text_input("사업체명", value=form_data["company_name"], key="company_name_1")
        form_data["company_address"] = st.text_input("주소", value=form_data["company_address"], key="company_address_1")
    with col2:
        form_data["business_number"] = st.text_input("사업자등록번호", value=form_data["business_number"], key="business_number_1")
        form_data["representative"] = st.text_input("대표자", value=form_data["representative"], key="representative_1")
    
    st.subheader("근로자 정보")
    col1, col2 = st.columns(2)
    with col1:
        form_data["employee_name"] = st.text_input("성명", value=form_data["employee_name"], key="employee_name_1")
        form_data["employee_address"] = st.text_input("주소", value=form_data["employee_address"], key="employee_address_1")
    with col2:
        form_data["employee_id_number"] = st.text_input("주민등록번호", value=form_data["employee_id_number"], key="employee_id_number_1")
        form_data["employee_phone"] = st.text_input("연락처", value=form_data["employee_phone"], key="employee_phone_1")
    
    st.subheader("근로 계약 기간")
    col1, col2 = st.columns(2)
    with col1:
        date_value = datetime.datetime.strptime(form_data["contract_start_date"], "%Y-%m-%d") if isinstance(form_data["contract_start_date"], str) else form_data["contract_start_date"]
        form_data["contract_start_date"] = st.date_input("계약 시작일", value=date_value, key="contract_start_date_1").strftime("%Y-%m-%d")
    with col2:
        is_indefinite = st.checkbox("기간의 정함이 없음", value=form_data["contract_end_date"] == "기간의 정함이 없음", key="indefinite_1")
        if is_indefinite:
            form_data["contract_end_date"] = "기간의 정함이 없음"
        else:
            end_date_value = datetime.datetime.strptime(form_data["contract_start_date"], "%Y-%m-%d") + datetime.timedelta(days=365) if form_data["contract_end_date"] == "기간의 정함이 없음" else datetime.datetime.strptime(form_data["contract_end_date"], "%Y-%m-%d")
            form_data["contract_end_date"] = st.date_input("계약 종료일", value=end_date_value, key="contract_end_date_1").strftime("%Y-%m-%d")
    
    st.subheader("근무 장소 및 업무 내용")
    col1, col2 = st.columns(2)
    with col1:
        form_data["work_place"] = st.text_input("근무 장소", value=form_data["work_place"], key="work_place_1")
    with col2:
        form_data["job_description"] = st.text_input("업무 내용", value=form_data["job_description"], key="job_description_1")
    
    st.subheader("근로 시간 및 휴게 시간")
    col1, col2, col3 = st.columns(3)
    with col1:
        form_data["work_start_time"] = st.text_input("근로 시작 시간", value=form_data["work_start_time"], key="work_start_time_1")
        form_data["work_days"] = st.text_input("근무일", value=form_data["work_days"], key="work_days_1")
    with col2:
        form_data["work_end_time"] = st.text_input("근로 종료 시간", value=form_data["work_end_time"], key="work_end_time_1")
        form_data["holidays"] = st.text_input("휴일", value=form_data["holidays"], key="holidays_1")
    with col3:
        form_data["break_time"] = st.text_input("휴게 시간", value=form_data["break_time"], key="break_time_1")
    
    st.subheader("임금")
    col1, col2 = st.columns(2)
    with col1:
        form_data["base_salary"] = st.text_input("기본급 (원)", value=form_data["base_salary"], key="base_salary_1")
        form_data["payment_day"] = st.text_input("임금 지급일 (매월 O일)", value=form_data["payment_day"], key="payment_day_1")
    with col2:
        form_data["bonus"] = st.text_input("상여금", value=form_data["bonus"], key="bonus_1")
        form_data["other_allowances"] = st.text_input("기타 수당", value=form_data["other_allowances"], key="other_allowances_1")
    
    st.subheader("사회보험 적용 여부")
    col1, col2 = st.columns(2)
    with col1:
        form_data["employment_insurance"] = st.checkbox("고용보험", value=form_data["employment_insurance"], key="employment_insurance_1")
        form_data["national_pension"] = st.checkbox("국민연금", value=form_data["national_pension"], key="national_pension_1")
    with col2:
        form_data["industrial_accident_insurance"] = st.checkbox("산재보험", value=form_data["industrial_accident_insurance"], key="industrial_accident_1")
        form_data["health_insurance"] = st.checkbox("건강보험", value=form_data["health_insurance"], key="health_insurance_1")
    
    st.subheader("기타 사항")
    form_data["other_terms"] = st.text_area("기타 계약 사항", value=form_data["other_terms"], height=100, key="other_terms_1")
    
    # 제출 버튼
    if st.button("근로계약서 생성", key="generate_contract_button"):
        # 세션 상태 업데이트
        for key in form_data:
            st.session_state.contract_data[key] = form_data[key]
        
        # 근로계약서 생성
        try:
            with st.spinner("근로계약서를 생성 중입니다..."):
                pdf_bytes = contract.generate_contract_pdf(st.session_state.contract_data)
                
                # PDF를 base64로 인코딩하여 다운로드 링크 생성
                b64 = base64.b64encode(pdf_bytes).decode()
                download_link = f'<a href="data:application/pdf;base64,{b64}" download="근로계약서_{st.session_state.contract_data["employee_name"]}.pdf">근로계약서 다운로드</a>'
                
                st.success("근로계약서가 성공적으로 생성되었습니다.")
                st.markdown(download_link, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"근로계약서 생성 중 오류가 발생했습니다: {e}")
            st.info("네트워크 연결 상태를 확인하고 다시 시도해 주세요.")

class EmploymentContract:
    """
    근로계약서 생성 클래스
    
    근로계약서 템플릿을 생성하고 PDF로 변환하는 기능을 제공합니다.
    """
    
    def __init__(self):
        # 한글 폰트 등록
        self.font_name = download_korean_font()
    
    def generate_contract_pdf(self, contract_data):
        """
        근로계약서 PDF 생성
        
        Args:
            contract_data (dict): 근로계약서 데이터
            
        Returns:
            bytes: PDF 파일 바이트 데이터
        """
        buffer = io.BytesIO()
        
        # PDF 문서 생성
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # 스타일 설정
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='Korean',
            fontName=self.font_name,
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY
        ))
        styles.add(ParagraphStyle(
            name='KoreanTitle',
            fontName=self.font_name,
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=10
        ))
        styles.add(ParagraphStyle(
            name='KoreanSubtitle',
            fontName=self.font_name,
            fontSize=12,
            leading=16,
            alignment=TA_LEFT,
            spaceAfter=6
        ))
        
        # 문서 내용
        story = []
        
        # 제목
        story.append(Paragraph("근 로 계 약 서", styles['KoreanTitle']))
        story.append(Spacer(1, 10*mm))
        
        # 사업주 정보
        story.append(Paragraph("1. 사업주", styles['KoreanSubtitle']))
        employer_info = f"""
        - 사업체명: {contract_data.get('company_name', '')}
        - 사업자등록번호: {contract_data.get('business_number', '')}
        - 주소: {contract_data.get('company_address', '')}
        - 대표자: {contract_data.get('representative', '')}
        """
        story.append(Paragraph(employer_info, styles['Korean']))
        story.append(Spacer(1, 5*mm))
        
        # 근로자 정보
        story.append(Paragraph("2. 근로자", styles['KoreanSubtitle']))
        employee_info = f"""
        - 성명: {contract_data.get('employee_name', '')}
        - 주민등록번호: {contract_data.get('employee_id_number', '')}
        - 주소: {contract_data.get('employee_address', '')}
        - 연락처: {contract_data.get('employee_phone', '')}
        """
        story.append(Paragraph(employee_info, styles['Korean']))
        story.append(Spacer(1, 5*mm))
