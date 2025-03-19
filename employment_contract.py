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
        # 시스템에 설치된 CJK 폰트 사용
        noto_font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
        wqy_font_path = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
        
        # 폰트 등록
        if os.path.exists(noto_font_path):
            pdfmetrics.registerFont(TTFont('NotoSansCJK', noto_font_path))
            font_name = 'NotoSansCJK'
        elif os.path.exists(wqy_font_path):
            pdfmetrics.registerFont(TTFont('WenQuanYiZenHei', wqy_font_path))
            font_name = 'WenQuanYiZenHei'
        else:
            # 폰트 파일이 없는 경우 다운로드
            font_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static/fonts")
            os.makedirs(font_dir, exist_ok=True)
            
            # NanumGothic 폰트 다운로드 (없는 경우)
            nanum_font_path = os.path.join(font_dir, "NanumGothic.ttf")
            if not os.path.exists(nanum_font_path):
                import urllib.request
                urllib.request.urlretrieve(
                    "https://github.com/naver/nanumfont/raw/master/NanumGothic.ttf",
                    nanum_font_path
                )
            
            # 폰트 등록
            pdfmetrics.registerFont(TTFont('NanumGothic', nanum_font_path))
            font_name = 'NanumGothic'
    
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
            fontName='NanumGothic',
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY
        ))
        styles.add(ParagraphStyle(
            name='KoreanTitle',
            fontName='NanumGothic',
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=10
        ))
        styles.add(ParagraphStyle(
            name='KoreanSubtitle',
            fontName='NanumGothic',
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
    
    # 폼 생성
    with st.form("employment_contract_form"):
        st.subheader("사업주 정보")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.contract_data["company_name"] = st.text_input(
                "사업체명",
                value=st.session_state.contract_data["company_name"]
            )
            st.session_state.contract_data["company_address"] = st.text_input(
                "주소",
                value=st.session_state.contract_data["company_address"]
            )
        with col2:
            st.session_state.contract_data["business_number"] = st.text_input(
                "사업자등록번호",
                value=st.session_state.contract_data["business_number"]
            )
            st.session_state.contract_data["representative"] = st.text_input(
                "대표자",
                value=st.session_state.contract_data["representative"]
            )
        
        st.subheader("근로자 정보")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.contract_data["employee_name"] = st.text_input(
                "성명",
                value=st.session_state.contract_data["employee_name"]
            )
            st.session_state.contract_data["employee_address"] = st.text_input(
                "주소",
                value=st.session_state.contract_data["employee_address"]
            )
        with col2:
            st.session_state.contract_data["employee_id_number"] = st.text_input(
                "주민등록번호",
                value=st.session_state.contract_data["employee_id_number"]
            )
            st.session_state.contract_data["employee_phone"] = st.text_input(
                "연락처",
                value=st.session_state.contract_data["employee_phone"]
            )
        
        st.subheader("근로 계약 기간")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.contract_data["contract_start_date"] = st.date_input(
                "계약 시작일",
                value=datetime.datetime.strptime(st.session_state.contract_data["contract_start_date"], "%Y-%m-%d") if isinstance(st.session_state.contract_data["contract_start_date"], str) else st.session_state.contract_data["contract_start_date"],
                format="YYYY-MM-DD"
            ).strftime("%Y-%m-%d")
        with col2:
            is_indefinite = st.checkbox("기간의 정함이 없음", value=st.session_state.contract_data["contract_end_date"] == "기간의 정함이 없음")
            if is_indefinite:
                st.session_state.contract_data["contract_end_date"] = "기간의 정함이 없음"
            else:
                st.session_state.contract_data["contract_end_date"] = st.date_input(
                    "계약 종료일",
                    value=datetime.datetime.strptime(st.session_state.contract_data["contract_start_date"], "%Y-%m-%d") + datetime.timedelta(days=365) if st.session_state.contract_data["contract_end_date"] == "기간의 정함이 없음" else datetime.datetime.strptime(st.session_state.contract_data["contract_end_date"], "%Y-%m-%d"),
                    format="YYYY-MM-DD"
                ).strftime("%Y-%m-%d")
        
        st.subheader("근무 장소 및 업무 내용")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.contract_data["work_place"] = st.text_input(
                "근무 장소",
                value=st.session_state.contract_data["work_place"]
            )
        with col2:
            st.session_state.contract_data["job_description"] = st.text_input(
                "업무 내용",
                value=st.session_state.contract_data["job_description"]
            )
        
        st.subheader("근로 시간 및 휴게 시간")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.session_state.contract_data["work_start_time"] = st.text_input(
                "근로 시작 시간",
                value=st.session_state.contract_data["work_start_time"]
            )
            st.session_state.contract_data["work_days"] = st.text_input(
                "근무일",
                value=st.session_state.contract_data["work_days"]
            )
        with col2:
            st.session_state.contract_data["work_end_time"] = st.text_input(
                "근로 종료 시간",
                value=st.session_state.contract_data["work_end_time"]
            )
            st.session_state.contract_data["holidays"] = st.text_input(
                "휴일",
                value=st.session_state.contract_data["holidays"]
            )
        with col3:
            st.session_state.contract_data["break_time"] = st.text_input(
                "휴게 시간",
                value=st.session_state.contract_data["break_time"]
            )
        
        st.subheader("임금")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.contract_data["base_salary"] = st.text_input(
                "기본급 (원)",
                value=st.session_state.contract_data["base_salary"]
            )
            st.session_state.contract_data["payment_day"] = st.text_input(
                "임금 지급일 (매월 O일)",
                value=st.session_state.contract_data["payment_day"]
            )
        with col2:
            st.session_state.contract_data["bonus"] = st.text_input(
                "상여금",
                value=st.session_state.contract_data["bonus"]
            )
            st.session_state.contract_data["other_allowances"] = st.text_input(
                "기타 수당",
                value=st.session_state.contract_data["other_allowances"]
            )
        
        st.subheader("사회보험 적용 여부")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.contract_data["employment_insurance"] = st.checkbox(
                "고용보험",
                value=st.session_state.contract_data["employment_insurance"]
            )
            st.session_state.contract_data["national_pension"] = st.checkbox(
                "국민연금",
                value=st.session_state.contract_data["national_pension"]
            )
        with col2:
            st.session_state.contract_data["industrial_accident_insurance"] = st.checkbox(
                "산재보험",
                value=st.session_state.contract_data["indus<response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>