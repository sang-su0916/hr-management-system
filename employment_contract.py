import streamlit as st
import os
import datetime
import base64
import requests

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
                html_content = contract.generate_contract_html(st.session_state.contract_data)
                
                # HTML을 base64로 인코딩하여 다운로드 링크 생성
                b64 = base64.b64encode(html_content.encode()).decode()
                download_link = f'<a href="data:text/html;base64,{b64}" download="근로계약서_{st.session_state.contract_data["employee_name"]}.html">근로계약서 다운로드</a>'
                
                st.success("근로계약서가 성공적으로 생성되었습니다.")
                st.markdown(download_link, unsafe_allow_html=True)
                
                # 생성된 HTML 미리보기 표시
                st.subheader("근로계약서 미리보기")
                st.components.v1.html(html_content, height=600, scrolling=True)
        except Exception as e:
            st.error(f"근로계약서 생성 중 오류가 발생했습니다: {e}")
            st.info("다시 시도해 주세요.")

class EmploymentContract:
    """
    근로계약서 생성 클래스
    
    근로계약서 템플릿을 생성하고 HTML로 변환하는 기능을 제공합니다.
    """
    
    def __init__(self):
        pass
    
    def generate_contract_html(self, contract_data):
        """
        근로계약서 HTML 생성
        
        Args:
            contract_data (dict): 근로계약서 데이터
            
        Returns:
            str: HTML 형식의 근로계약서
        """
        # CSS 스타일 정의
        css_style = """
        <style>
            body {
                font-family: 'Malgun Gothic', 'Gulim', sans-serif;
                line-height: 1.6;
                margin: 40px;
                color: #333;
            }
            h1 {
                text-align: center;
                font-size: 24px;
                margin-bottom: 30px;
            }
            h2 {
                font-size: 18px;
                margin-top: 20px;
                margin-bottom: 10px;
                border-bottom: 1px solid #ccc;
                padding-bottom: 5px;
            }
            .contract-section {
                margin-bottom: 20px;
            }
            .signature {
                margin-top: 40px;
                text-align: center;
            }
            .signature-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            .signature-table td {
                padding: 10px;
                vertical-align: top;
            }
            ul {
                list-style-type: none;
                padding-left: 0;
            }
            li {
                margin-bottom: 8px;
                padding-left: 20px;
                position: relative;
            }
            li:before {
                content: "-";
                position: absolute;
                left: 0;
            }
            .print-button {
                text-align: center;
                margin: 20px;
            }
            @media print {
                .print-button {
                    display: none;
                }
                body {
                    margin: 0;
                    padding: 20px;
                }
            }
        </style>
        """
        
        # 인쇄 기능 JavaScript
        print_script = """
        <script>
            function printContract() {
                window.print();
            }
        </script>
        """
        
        # HTML 문서 시작
        html = f"""
        <!DOCTYPE html>
        <html lang="ko">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>근로계약서 - {contract_data.get('employee_name', '')}</title>
            {css_style}
            {print_script}
        </head>
        <body>
            <div class="print-button">
                <button onclick="printContract()">인쇄하기</button>
            </div>
            
            <h1>근 로 계 약 서</h1>
            
            <div class="contract-section">
                <h2>1. 사업주</h2>
                <ul>
                    <li>사업체명: {contract_data.get('company_name', '')}</li>
                    <li>사업자등록번호: {contract_data.get('business_number', '')}</li>
                    <li>주소: {contract_data.get('company_address', '')}</li>
                    <li>대표자: {contract_data.get('representative', '')}</li>
                </ul>
            </div>
            
            <div class="contract-section">
                <h2>2. 근로자</h2>
                <ul>
                    <li>성명: {contract_data.get('employee_name', '')}</li>
                    <li>주민등록번호: {contract_data.get('employee_id_number', '')}</li>
                    <li>주소: {contract_data.get('employee_address', '')}</li>
                    <li>연락처: {contract_data.get('employee_phone', '')}</li>
                </ul>
            </div>
            
            <div class="contract-section">
                <h2>3. 근로 계약 기간</h2>
                <ul>
                    <li>근로계약기간: {contract_data.get('contract_start_date', '')} ~ {contract_data.get('contract_end_date', '기간의 정함이 없음')}</li>
                </ul>
            </div>
            
            <div class="contract-section">
                <h2>4. 근무 장소 및 업무 내용</h2>
                <ul>
                    <li>근무 장소: {contract_data.get('work_place', '')}</li>
                    <li>업무 내용: {contract_data.get('job_description', '')}</li>
                </ul>
            </div>
            
            <div class="contract-section">
                <h2>5. 근로 시간 및 휴게 시간</h2>
                <ul>
                    <li>근로시간: {contract_data.get('work_start_time', '')} ~ {contract_data.get('work_end_time', '')}</li>
                    <li>휴게시간: {contract_data.get('break_time', '')}</li>
                    <li>근무일/휴일: {contract_data.get('work_days', '')} / {contract_data.get('holidays', '')}</li>
                </ul>
            </div>
            
            <div class="contract-section">
                <h2>6. 임금</h2>
                <ul>
                    <li>기본급: {contract_data.get('base_salary', '')}원</li>
                    <li>상여금: {contract_data.get('bonus', '')}</li>
                    <li>기타 수당: {contract_data.get('other_allowances', '')}</li>
                    <li>임금 지급일: 매월 {contract_data.get('payment_day', '')}일</li>
                    <li>지급 방법: {contract_data.get('payment_method', '근로자 명의 예금통장에 입금')}</li>
                </ul>
            </div>
            
            <div class="contract-section">
                <h2>7. 사회보험 적용 여부</h2>
                <ul>
                    <li>고용보험: {'적용' if contract_data.get('employment_insurance', True) else '미적용'}</li>
                    <li>산재보험: {'적용' if contract_data.get('industrial_accident_insurance', True) else '미적용'}</li>
                    <li>국민연금: {'적용' if contract_data.get('national_pension', True) else '미적용'}</li>
                    <li>건강보험: {'적용' if contract_data.get('health_insurance', True) else '미적용'}</li>
                </ul>
            </div>
            
            <div class="contract-section">
                <h2>8. 휴가</h2>
                <ul>
                    <li>연차유급휴가: 근로기준법에 따라 부여</li>
                    <li>경조사휴가: 회사 규정에 따라 부여</li>
                </ul>
            </div>
            
            <div class="contract-section">
                <h2>9. 기타</h2>
                <ul>
                    <li>이 계약에 정함이 없는 사항은 근로기준법 및 회사 취업규칙에 따릅니다.</li>
                    <li>{contract_data.get('other_terms', '')}</li>
                </ul>
            </div>
            
            <div class="signature">
                {datetime.date.today().strftime("%Y년 %m월 %d일")}
                
                <table class="signature-table">
                    <tr>
                        <td width="50%">
                            <p><b>(사업주)</b></p>
                            <p>주소: {contract_data.get('company_address', '')}</p>
                            <p>성명: {contract_data.get('representative', '')} (서명 또는 인)</p>
                        </td>
                        <td width="50%">
                            <p><b>(근로자)</b></p>
                            <p>주소: {contract_data.get('employee_address', '')}</p>
                            <p>성명: {contract_data.get('employee_name', '')} (서명 또는 인)</p>
                        </td>
                    </tr>
                </table>
            </div>
        </body>
        </html>
        """
        
        return html
    
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
