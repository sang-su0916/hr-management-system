import streamlit as st
import datetime
import io
import base64
import os
import pandas as pd
import numpy as np

def render_pay_statement_ui():
    """
    임금명세서 UI 렌더링 함수
    """
    st.title("💵 임금명세서 생성기")
    
    # 기본 템플릿 데이터 초기화
    if 'pay_statement_data' not in st.session_state:
        st.session_state.pay_statement_data = get_pay_statement_template()
    
    # 폼 데이터를 위한 임시 변수
    form_data = {}
    for key in st.session_state.pay_statement_data:
        form_data[key] = st.session_state.pay_statement_data[key]
    
    # 임금명세서 정보 입력 폼
    st.subheader("기본 정보")
    col1, col2 = st.columns(2)
    
    with col1:
        form_data["company_name"] = st.text_input("회사명", value=form_data["company_name"], key="company_name_pay")
        form_data["employee_name"] = st.text_input("직원명", value=form_data["employee_name"], key="employee_name_pay")
        form_data["department"] = st.text_input("부서", value=form_data["department"], key="department_pay")
    
    with col2:
        form_data["pay_period"] = st.text_input("급여 기간", value=form_data["pay_period"], key="pay_period_pay")
        form_data["pay_date"] = st.date_input("지급일", value=datetime.datetime.strptime(form_data["pay_date"], "%Y-%m-%d") if isinstance(form_data["pay_date"], str) else form_data["pay_date"], key="pay_date_pay").strftime("%Y-%m-%d")
        form_data["position"] = st.text_input("직위", value=form_data["position"], key="position_pay")
    
    # 급여 항목
    st.subheader("급여 항목")
    col1, col2 = st.columns(2)
    
    with col1:
        form_data["base_salary"] = st.number_input("기본급", value=int(form_data["base_salary"]) if form_data["base_salary"] else 0, min_value=0, step=10000, key="base_salary_pay")
        form_data["overtime_pay"] = st.number_input("초과근무수당", value=int(form_data["overtime_pay"]) if form_data["overtime_pay"] else 0, min_value=0, step=10000, key="overtime_pay_pay")
        form_data["bonus"] = st.number_input("상여금", value=int(form_data["bonus"]) if form_data["bonus"] else 0, min_value=0, step=10000, key="bonus_pay")
        form_data["meal_allowance"] = st.number_input("식대", value=int(form_data["meal_allowance"]) if form_data["meal_allowance"] else 0, min_value=0, step=10000, key="meal_allowance_pay")
        form_data["transportation_allowance"] = st.number_input("교통비", value=int(form_data["transportation_allowance"]) if form_data["transportation_allowance"] else 0, min_value=0, step=10000, key="transportation_allowance_pay")
        form_data["other_allowance"] = st.number_input("기타 수당", value=int(form_data["other_allowance"]) if form_data["other_allowance"] else 0, min_value=0, step=10000, key="other_allowance_pay")
    
    # 공제 항목
    st.subheader("공제 항목")
    with col2:
        form_data["income_tax"] = st.number_input("소득세", value=int(form_data["income_tax"]) if form_data["income_tax"] else 0, min_value=0, step=1000, key="income_tax_pay")
        form_data["local_income_tax"] = st.number_input("지방소득세", value=int(form_data["local_income_tax"]) if form_data["local_income_tax"] else 0, min_value=0, step=1000, key="local_income_tax_pay")
        form_data["national_pension"] = st.number_input("국민연금", value=int(form_data["national_pension"]) if form_data["national_pension"] else 0, min_value=0, step=1000, key="national_pension_pay")
        form_data["health_insurance"] = st.number_input("건강보험", value=int(form_data["health_insurance"]) if form_data["health_insurance"] else 0, min_value=0, step=1000, key="health_insurance_pay")
        form_data["employment_insurance"] = st.number_input("고용보험", value=int(form_data["employment_insurance"]) if form_data["employment_insurance"] else 0, min_value=0, step=1000, key="employment_insurance_pay")
        form_data["other_deduction"] = st.number_input("기타 공제", value=int(form_data["other_deduction"]) if form_data["other_deduction"] else 0, min_value=0, step=1000, key="other_deduction_pay")
    
    # 자동 계산
    total_salary = (form_data["base_salary"] + form_data["overtime_pay"] + form_data["bonus"] + 
                    form_data["meal_allowance"] + form_data["transportation_allowance"] + form_data["other_allowance"])
    
    total_deduction = (form_data["income_tax"] + form_data["local_income_tax"] + form_data["national_pension"] + 
                       form_data["health_insurance"] + form_data["employment_insurance"] + form_data["other_deduction"])
    
    net_salary = total_salary - total_deduction
    
    # 합계 표시
    st.subheader("급여 합계")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("총 지급액", f"{total_salary:,}원")
        form_data["total_salary"] = total_salary
    
    with col2:
        st.metric("총 공제액", f"{total_deduction:,}원")
        form_data["total_deduction"] = total_deduction
    
    with col3:
        st.metric("실수령액", f"{net_salary:,}원")
        form_data["net_salary"] = net_salary
    
    # 비고
    st.subheader("비고")
    form_data["remarks"] = st.text_area("비고", value=form_data["remarks"], height=100, key="remarks_pay")
    
    # 생성 버튼
    if st.button("임금명세서 생성", key="generate_pay_statement"):
        # 세션 상태 업데이트
        for key in form_data:
            st.session_state.pay_statement_data[key] = form_data[key]
        
        # 임금명세서 생성
        try:
            with st.spinner("임금명세서를 생성 중입니다..."):
                # HTML 임금명세서 생성
                html_content = generate_pay_statement_html(st.session_state.pay_statement_data)
                
                # HTML을 base64로 인코딩하여 다운로드 링크 생성
                b64 = base64.b64encode(html_content.encode()).decode()
                download_link = f'<a href="data:text/html;base64,{b64}" download="임금명세서_{st.session_state.pay_statement_data["employee_name"]}_{st.session_state.pay_statement_data["pay_period"]}.html">임금명세서 다운로드</a>'
                
                st.success("임금명세서가 성공적으로 생성되었습니다.")
                st.markdown(download_link, unsafe_allow_html=True)
                
                # 생성된 HTML 미리보기 표시
                st.subheader("임금명세서 미리보기")
                st.components.v1.html(html_content, height=600, scrolling=True)
        except Exception as e:
            st.error(f"임금명세서 생성 중 오류가 발생했습니다: {e}")

def generate_pay_statement_html(data):
    """
    HTML 임금명세서 생성
    
    Args:
        data (dict): 임금명세서 데이터
        
    Returns:
        str: HTML 형식의 임금명세서
    """
    # 한국어 통화 포맷 함수
    def format_currency(value):
        if value is None:
            return "0원"
        return f"{int(value):,}원"
    
    # CSS 스타일 정의
    css_style = """
    <style>
        body {
            font-family: 'Malgun Gothic', 'Gulim', sans-serif;
            line-height: 1.6;
            margin: 40px;
            color: #333;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            border: 1px solid #ddd;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            font-size: 24px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }
        .header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .company-info, .employee-info {
            flex: 1;
        }
        .info-item {
            margin-bottom: 5px;
        }
        .info-label {
            font-weight: bold;
            display: inline-block;
            width: 100px;
        }
        .section-title {
            font-size: 18px;
            margin: 20px 0 10px;
            padding-bottom: 5px;
            border-bottom: 1px solid #eee;
        }
        .pay-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .pay-table th, .pay-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .pay-table th {
            background-color: #f8f9fa;
        }
        .summary {
            display: flex;
            justify-content: space-between;
            margin: 20px 0;
            font-weight: bold;
        }
        .summary-item {
            text-align: center;
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
        }
        .total {
            background-color: #e8f4fd;
        }
        .remarks {
            margin-top: 20px;
            border: 1px solid #ddd;
            padding: 10px;
            background-color: #f9f9f9;
        }
        .footer {
            margin-top: 30px;
            text-align: center;
            font-size: 14px;
            color: #777;
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
        function printPayStatement() {
            window.print();
        }
    </script>
    """
    
    # HTML 문서 생성
    html = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>임금명세서 - {data.get('employee_name', '')} ({data.get('pay_period', '')})</title>
        {css_style}
        {print_script}
    </head>
    <body>
        <div class="print-button">
            <button onclick="printPayStatement()">인쇄하기</button>
        </div>
        
        <div class="container">
            <h1>임 금 명 세 서</h1>
            
            <div class="header">
                <div class="company-info">
                    <div class="info-item"><span class="info-label">회사명</span>: {data.get('company_name', '')}</div>
                    <div class="info-item"><span class="info-label">급여 기간</span>: {data.get('pay_period', '')}</div>
                    <div class="info-item"><span class="info-label">지급일</span>: {data.get('pay_date', '')}</div>
                </div>
                <div class="employee-info">
                    <div class="info-item"><span class="info-label">직원명</span>: {data.get('employee_name', '')}</div>
                    <div class="info-item"><span class="info-label">부서</span>: {data.get('department', '')}</div>
                    <div class="info-item"><span class="info-label">직위</span>: {data.get('position', '')}</div>
                </div>
            </div>
            
            <h2 class="section-title">급여 내역</h2>
            <table class="pay-table">
                <tr>
                    <th>항목</th>
                    <th>금액</th>
                    <th>비고</th>
                </tr>
                <tr>
                    <td>기본급</td>
                    <td>{format_currency(data.get('base_salary', 0))}</td>
                    <td></td>
                </tr>
                <tr>
                    <td>초과근무수당</td>
                    <td>{format_currency(data.get('overtime_pay', 0))}</td>
                    <td></td>
                </tr>
                <tr>
                    <td>상여금</td>
                    <td>{format_currency(data.get('bonus', 0))}</td>
                    <td></td>
                </tr>
                <tr>
                    <td>식대</td>
                    <td>{format_currency(data.get('meal_allowance', 0))}</td>
                    <td></td>
                </tr>
                <tr>
                    <td>교통비</td>
                    <td>{format_currency(data.get('transportation_allowance', 0))}</td>
                    <td></td>
                </tr>
                <tr>
                    <td>기타 수당</td>
                    <td>{format_currency(data.get('other_allowance', 0))}</td>
                    <td></td>
                </tr>
            </table>
            
            <h2 class="section-title">공제 내역</h2>
            <table class="pay-table">
                <tr>
                    <th>항목</th>
                    <th>금액</th>
                    <th>비고</th>
                </tr>
                <tr>
                    <td>소득세</td>
                    <td>{format_currency(data.get('income_tax', 0))}</td>
                    <td></td>
                </tr>
                <tr>
                    <td>지방소득세</td>
                    <td>{format_currency(data.get('local_income_tax', 0))}</td>
                    <td></td>
                </tr>
                <tr>
                    <td>국민연금</td>
                    <td>{format_currency(data.get('national_pension', 0))}</td>
                    <td></td>
                </tr>
                <tr>
                    <td>건강보험</td>
                    <td>{format_currency(data.get('health_insurance', 0))}</td>
                    <td></td>
                </tr>
                <tr>
                    <td>고용보험</td>
                    <td>{format_currency(data.get('employment_insurance', 0))}</td>
                    <td></td>
                </tr>
                <tr>
                    <td>기타 공제</td>
                    <td>{format_currency(data.get('other_deduction', 0))}</td>
                    <td></td>
                </tr>
            </table>
            
            <div class="summary">
                <div class="summary-item">
                    <div>총 지급액</div>
                    <div>{format_currency(data.get('total_salary', 0))}</div>
                </div>
                <div class="summary-item">
                    <div>총 공제액</div>
                    <div>{format_currency(data.get('total_deduction', 0))}</div>
                </div>
                <div class="summary-item total">
                    <div>실수령액</div>
                    <div>{format_currency(data.get('net_salary', 0))}</div>
                </div>
            </div>
            
            <div class="remarks">
                <h3>비고</h3>
                <p>{data.get('remarks', '').replace('\n', '<br>')}</p>
            </div>
            
            <div class="footer">
                <p>본 임금명세서는 {datetime.datetime.now().strftime("%Y년 %m월 %d일")}에 생성되었습니다.</p>
                <p>{data.get('company_name', '')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def get_pay_statement_template():
    """
    임금명세서 기본 템플릿 데이터 반환
    
    Returns:
        dict: 임금명세서 기본 템플릿 데이터
    """
    today = datetime.date.today()
    current_month = today.replace(day=1)
    last_month = (current_month - datetime.timedelta(days=1)).replace(day=1)
    pay_period = f"{last_month.year}년 {last_month.month}월"
    
    return {
        # 기본 정보
        "company_name": "",
        "employee_name": "",
        "department": "",
        "position": "",
        "pay_period": pay_period,
        "pay_date": today.strftime("%Y-%m-%d"),
        
        # 급여 항목
        "base_salary": 0,
        "overtime_pay": 0,
        "bonus": 0,
        "meal_allowance": 0,
        "transportation_allowance": 0,
        "other_allowance": 0,
        
        # 공제 항목
        "income_tax": 0,
        "local_income_tax": 0,
        "national_pension": 0,
        "health_insurance": 0,
        "employment_insurance": 0,
        "other_deduction": 0,
        
        # 합계
        "total_salary": 0,
        "total_deduction": 0,
        "net_salary": 0,
        
        # 비고
        "remarks": ""
    }
