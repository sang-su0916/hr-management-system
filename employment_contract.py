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
        pdf_bytes = contract.generate_contract_pdf(st.session_state.contract_data)
        
        # PDF를 base64로 인코딩하여 다운로드 링크 생성
        b64 = base64.b64encode(pdf_bytes).decode()
        download_link = f'<a href="data:application/pdf;base64,{b64}" download="근로계약서_{st.session_state.contract_data["employee_name"]}.pdf">근로계약서 다운로드</a>'
        
        st.success("근로계약서가 성공적으로 생성되었습니다.")
        st.markdown(download_link, unsafe_allow_html=True)

class EmploymentContract:
    """
    근로계약서 생성 클래스
    
    근로계약서 템플릿을 생성하고 PDF로 변환하는 기능을 제공합니다.
    """
    
    def __init__(self):
        # 한글 폰트 등록 (기본 폰트가 한글을 지원하지 않을 수 있음)
        self._register_korean_fonts()
    
    def _register_korean_fonts(self):
        """한글 폰트 등록"""
        # 시스템에 설치된 CJK 폰트 검색
        try:
            # 기본 폰트 목록
            font_paths = [
                "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
                "/usr/share/fonts/truetype/unbatang/UnBatang.ttf",
                "/usr/share/fonts/open-sans/OpenSans-Regular.ttf"
            ]
            
            # 폰트 찾기 및 등록
            font_found = False
            for font_path in font_paths:
                if os.path.exists(font_path):
                    font_name = os.path.basename(font_path).split('.')[0]
                    pdfmetrics.registerFont(TTFont(font_name, font_path))
                    font_found = True
                    break
            
            # 폰트를 찾지 못한 경우 기본 폰트 사용
            if not font_found:
                # Helvetica는 ReportLab에 기본으로 내장되어 있음
                # 한글이 제대로 표시되지 않을 수 있지만 오류는 방지
                pass
        except Exception as e:
            st.warning(f"폰트 등록 중 오류가 발생했습니다: {e}")
            st.warning("한글이 제대로 표시되지 않을 수 있습니다.")
    
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
            fontName='Helvetica',  # 기본 폰트 사용
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY
        ))
        styles.add(ParagraphStyle(
            name='KoreanTitle',
            fontName='Helvetica',  # 기본 폰트 사용
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=10
        ))
        styles.add(ParagraphStyle(
            name='KoreanSubtitle',
            fontName='Helvetica',  # 기본 폰트 사용
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
        
        # 근로 계약 기간
        story.append(Paragraph("3. 근로 계약 기간", styles['KoreanSubtitle']))
        contract_period = f"""
        - 근로계약기간: {contract_data.get('contract_start_date', '')} ~ {contract_data.get('contract_end_date', '기간의 정함이 없음')}
        """
        story.append(Paragraph(contract_period, styles['Korean']))
        story.append(Spacer(1, 5*mm))
        
        # 근무 장소 및 업무 내용
        story.append(Paragraph("4. 근무 장소 및 업무 내용", styles['KoreanSubtitle']))
        work_info = f"""
        - 근무 장소: {contract_data.get('work_place', '')}
        - 업무 내용: {contract_data.get('job_description', '')}
        """
        story.append(Paragraph(work_info, styles['Korean']))
        story.append(Spacer(1, 5*mm))
        
        # 근로 시간 및 휴게 시간
        story.append(Paragraph("5. 근로 시간 및 휴게 시간", styles['KoreanSubtitle']))
        work_time = f"""
        - 근로시간: {contract_data.get('work_start_time', '')} ~ {contract_data.get('work_end_time', '')}
        - 휴게시간: {contract_data.get('break_time', '')}
        - 근무일/휴일: {contract_data.get('work_days', '')} / {contract_data.get('holidays', '')}
        """
        story.append(Paragraph(work_time, styles['Korean']))
        story.append(Spacer(1, 5*mm))
        
        # 임금
        story.append(Paragraph("6. 임금", styles['KoreanSubtitle']))
        salary_info = f"""
        - 기본급: {contract_data.get('base_salary', '')}원
        - 상여금: {contract_data.get('bonus', '')}
        - 기타 수당: {contract_data.get('other_allowances', '')}
        - 임금 지급일: 매월 {contract_data.get('payment_day', '')}일
        - 지급 방법: {contract_data.get('payment_method', '근로자 명의 예금통장에 입금')}
        """
        story.append(Paragraph(salary_info, styles['Korean']))
        story.append(Spacer(1, 5*mm))
        
        # 사회보험 적용
        story.append(Paragraph("7. 사회보험 적용 여부", styles['KoreanSubtitle']))
        insurance_info = f"""
        - 고용보험: {'적용' if contract_data.get('employment_insurance', True) else '미적용'}
        - 산재보험: {'적용' if contract_data.get('industrial_accident_insurance', True) else '미적용'}
        - 국민연금: {'적용' if contract_data.get('national_pension', True) else '미적용'}
        - 건강보험: {'적용' if contract_data.get('health_insurance', True) else '미적용'}
        """
        story.append(Paragraph(insurance_info, styles['Korean']))
        story.append(Spacer(1, 5*mm))
        
        # 휴가
        story.append(Paragraph("8. 휴가", styles['KoreanSubtitle']))
        vacation_info = f"""
        - 연차유급휴가: 근로기준법에 따라 부여
        - 경조사휴가: 회사 규정에 따라 부여
        """
        story.append(Paragraph(vacation_info, styles['Korean']))
        story.append(Spacer(1, 5*mm))
        
        # 기타
        story.append(Paragraph("9. 기타", styles['KoreanSubtitle']))
        other_info = f"""
        - 이 계약에 정함이 없는 사항은 근로기준법 및 회사 취업규칙에 따릅니다.
        - {contract_data.get('other_terms', '')}
        """
        story.append(Paragraph(other_info, styles['Korean']))
        story.append(Spacer(1, 10*mm))
        
        # 서명
        today = datetime.date.today().strftime("%Y년 %m월 %d일")
        signature = f"""
        {today}
        
        (사업주) 주소: {contract_data.get('company_address', '')}
                성명: {contract_data.get('representative', '')} (서명 또는 인)
                
        (근로자) 주소: {contract_data.get('employee_address', '')}
                성명: {contract_data.get('employee_name', '')} (서명 또는 인)
        """
        story.append(Paragraph(signature, styles['Korean']))
        
        # PDF 생성
        doc.build(story)
        
        # 버퍼의 내용을 바이트로 변환
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def get_contract_template(self):
        """
        근로계약서 기본 템플릿 데이터 반환
        
        Returns:
            dict: 근로계약서 기본 템플릿 데이터
        """
        today = datetime.date.today()
        
        return {
            # 사업주 정보
            "company_name": "",
            "business_number": "",
            "company_address": "",
            "representative": "",
            
            # 근로자 정보
            "employee_name": "",
            "employee_id_number": "",
            "employee_address": "",
            "employee_phone": "",
            
            # 근로 계약 기간
            "contract_start_date": today.strftime("%Y-%m-%d"),
            "contract_end_date": "기간의 정함이 없음",
            
            # 근무 장소 및 업무 내용
            "work_place": "",
            "job_description": "",
            
            # 근로 시간 및 휴게 시간
            "work_start_time": "09:00",
            "work_end_time": "18:00",
            "break_time": "12:00~13:00",
            "work_days": "월~금",
            "holidays": "토, 일, 공휴일",
            
            # 임금
            "base_salary": "",
            "bonus": "없음",
            "other_allowances": "없음",
            "payment_day": "25",
            "payment_method": "근로자 명의 예금통장에 입금",
            
            # 사회보험 적용 여부
            "employment_insurance": True,
            "industrial_accident_insurance": True,
            "national_pension": True,
            "health_insurance": True,
            
            # 기타
            "other_terms": ""
        }
