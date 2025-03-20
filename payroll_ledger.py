import pandas as pd
import numpy as np
import datetime
import os
import uuid
import json
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

class PayrollLedger:
    """
    임금대장 시스템 클래스
    
    임금대장 데이터 모델 및 관리 기능을 제공합니다.
    """
    
    def __init__(self, data_dir=None):
        """
        임금대장 시스템 초기화
        
        Args:
            data_dir (str, optional): 데이터 저장 디렉토리. 기본값은 None.
        """
        if data_dir is None:
            self.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
        else:
            self.data_dir = data_dir
        
        # 데이터 디렉토리 생성
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 임금대장 파일 경로
        self.ledger_file = os.path.join(self.data_dir, "payroll_ledger.csv")
        self.employee_file = os.path.join(self.data_dir, "employees.csv")
        
        # 임금대장 데이터 로드
        self.load_data()
    
    def load_data(self):
        """
        임금대장 데이터 로드
        """
        # 직원 정보 로드
        if os.path.exists(self.employee_file):
            self.employees = pd.read_csv(self.employee_file)
        else:
            self.employees = pd.DataFrame({
                "employee_id": [],
                "name": [],
                "department": [],
                "position": [],
                "entry_date": [],
                "base_salary": [],
                "hourly_rate": [],
                "payment_type": []  # 'monthly' 또는 'hourly'
            })
        
        # 임금대장 로드
        if os.path.exists(self.ledger_file):
            self.ledger = pd.read_csv(self.ledger_file)
            
            # 날짜 형식 변환
            if 'payment_date' in self.ledger.columns:
                self.ledger['payment_date'] = pd.to_datetime(self.ledger['payment_date'])
        else:
            self.ledger = pd.DataFrame({
                "ledger_id": [],
                "employee_id": [],
                "payment_date": [],
                "payment_period_start": [],
                "payment_period_end": [],
                "base_salary": [],
                "overtime_hours": [],
                "overtime_pay": [],
                "bonus": [],
                "meal_allowance": [],
                "transportation_allowance": [],
                "other_allowances": [],
                "gross_pay": [],
                "income_tax": [],
                "local_income_tax": [],
                "national_pension": [],
                "health_insurance": [],
                "employment_insurance": [],
                "total_deductions": [],
                "net_pay": [],
                "payment_method": [],
                "note": []
            })
    
    def save_data(self):
        """
        임금대장 데이터 저장
        """
        self.employees.to_csv(self.employee_file, index=False)
        self.ledger.to_csv(self.ledger_file, index=False)
    
    def add_employee(self, employee_data):
        """
        직원 추가
        
        Args:
            employee_data (dict): 직원 정보
            
        Returns:
            str: 직원 ID
        """
        # 직원 ID 생성
        employee_id = str(uuid.uuid4())[:8]
        
        # 직원 정보 추가
        employee = {
            "employee_id": employee_id,
            "name": employee_data.get("name", ""),
            "department": employee_data.get("department", ""),
            "position": employee_data.get("position", ""),
            "entry_date": employee_data.get("entry_date", ""),
            "base_salary": employee_data.get("base_salary", 0),
            "hourly_rate": employee_data.get("hourly_rate", 0),
            "payment_type": employee_data.get("payment_type", "monthly")
        }
        
        # 직원 정보 추가
        self.employees = pd.concat([self.employees, pd.DataFrame([employee])], ignore_index=True)
        
        # 데이터 저장
        self.save_data()
        
        return employee_id
    
    def update_employee(self, employee_id, employee_data):
        """
        직원 정보 업데이트
        
        Args:
            employee_id (str): 직원 ID
            employee_data (dict): 업데이트할 직원 정보
            
        Returns:
            bool: 업데이트 성공 여부
        """
        # 직원 정보 찾기
        employee_idx = self.employees[self.employees["employee_id"] == employee_id].index
        
        if len(employee_idx) == 0:
            return False
        
        # 직원 정보 업데이트
        for key, value in employee_data.items():
            if key in self.employees.columns:
                self.employees.loc[employee_idx, key] = value
        
        # 데이터 저장
        self.save_data()
        
        return True
    
    def delete_employee(self, employee_id):
        """
        직원 삭제
        
        Args:
            employee_id (str): 직원 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        # 직원 정보 찾기
        employee_idx = self.employees[self.employees["employee_id"] == employee_id].index
        
        if len(employee_idx) == 0:
            return False
        
        # 직원 정보 삭제
        self.employees = self.employees.drop(employee_idx)
        
        # 해당 직원의 임금대장 기록 삭제
        ledger_idx = self.ledger[self.ledger["employee_id"] == employee_id].index
        self.ledger = self.ledger.drop(ledger_idx)
        
        # 데이터 저장
        self.save_data()
        
        return True
    
    def get_employee(self, employee_id):
        """
        직원 정보 조회
        
        Args:
            employee_id (str): 직원 ID
            
        Returns:
            dict: 직원 정보
        """
        employee = self.employees[self.employees["employee_id"] == employee_id]
        
        if len(employee) == 0:
            return None
        
        return employee.iloc[0].to_dict()
    
    def get_all_employees(self):
        """
        모든 직원 정보 조회
        
        Returns:
            pandas.DataFrame: 모든 직원 정보
        """
        return self.employees
    
    def add_payroll(self, payroll_data):
        """
        임금 지급 기록 추가
        
        Args:
            payroll_data (dict): 임금 지급 정보
            
        Returns:
            str: 임금 지급 ID
        """
        # 임금 지급 ID 생성
        ledger_id = str(uuid.uuid4())[:8]
        
        # 직원 정보 확인
        employee_id = payroll_data.get("employee_id", "")
        employee = self.get_employee(employee_id)
        
        if employee is None:
            return None
        
        # 기본급 설정
        base_salary = payroll_data.get("base_salary", employee["base_salary"])
        
        # 총 급여 계산
        overtime_pay = payroll_data.get("overtime_pay", 0)
        bonus = payroll_data.get("bonus", 0)
        meal_allowance = payroll_data.get("meal_allowance", 0)
        transportation_allowance = payroll_data.get("transportation_allowance", 0)
        other_allowances = payroll_data.get("other_allowances", 0)
        
        gross_pay = base_salary + overtime_pay + bonus + meal_allowance + transportation_allowance + other_allowances
        
        # 공제액 계산
        income_tax = payroll_data.get("income_tax", gross_pay * 0.03)  # 소득세 (기본 3%)
        local_income_tax = payroll_data.get("local_income_tax", income_tax * 0.1)  # 지방소득세 (소득세의 10%)
        national_pension = payroll_data.get("national_pension", gross_pay * 0.045)  # 국민연금 (4.5%)
        health_insurance = payroll_data.get("health_insurance", gross_pay * 0.0343)  # 건강보험 (3.43%)
        employment_insurance = payroll_data.get("employment_insurance", gross_pay * 0.008)  # 고용보험 (0.8%)
        
        total_deductions = income_tax + local_income_tax + national_pension + health_insurance + employment_insurance
        
        # 실수령액 계산
        net_pay = gross_pay - total_deductions
        
        # 임금 지급 정보 추가
        payroll = {
            "ledger_id": ledger_id,
            "employee_id": employee_id,
            "payment_date": payroll_data.get("payment_date", datetime.date.today().strftime("%Y-%m-%d")),
            "payment_period_start": payroll_data.get("payment_period_start", ""),
            "payment_period_end": payroll_data.get("payment_period_end", ""),
            "base_salary": base_salary,
            "overtime_hours": payroll_data.get("overtime_hours", 0),
            "overtime_pay": overtime_pay,
            "bonus": bonus,
            "meal_allowance": meal_allowance,
            "transportation_allowance": transportation_allowance,
            "other_allowances": other_allowances,
            "gross_pay": gross_pay,
            "income_tax": income_tax,
            "local_income_tax": local_income_tax,
            "national_pension": national_pension,
            "health_insurance": health_insurance,
            "employment_insurance": employment_insurance,
            "total_deductions": total_deductions,
            "net_pay": net_pay,
            "payment_method": payroll_data.get("payment_method", "계좌이체"),
            "note": payroll_data.get("note", "")
        }
        
        # 임금 지급 정보 추가
        self.ledger = pd.concat([self.ledger, pd.DataFrame([payroll])], ignore_index=True)
        
        # 데이터 저장
        self.save_data()
        
        return ledger_id
    
    def update_payroll(self, ledger_id, payroll_data):
        """
        임금 지급 기록 업데이트
        
        Args:
            ledger_id (str): 임금 지급 ID
            payroll_data (dict): 업데이트할 임금 지급 정보
            
        Returns:
            bool: 업데이트 성공 여부
        """
        # 임금 지급 정보 찾기
        payroll_idx = self.ledger[self.ledger["ledger_id"] == ledger_id].index
        
        if len(payroll_idx) == 0:
            return False
        
        # 직원 정보 확인
        employee_id = self.ledger.loc[payroll_idx[0], "employee_id"]
        employee = self.get_employee(employee_id)
        
        if employee is None:
            return False
        
        # 기본급 설정
        base_salary = payroll_data.get("base_salary", self.ledger.loc[payroll_idx[0], "base_salary"])
        
        # 총 급여 계산
        overtime_pay = payroll_data.get("overtime_pay", self.ledger.loc[payroll_idx[0], "overtime_pay"])
        bonus = payroll_data.get("bonus", self.ledger.loc[payroll_idx[0], "bonus"])
        meal_allowance = payroll_data.get("meal_allowance", self.ledger.loc[payroll_idx[0], "meal_allowance"])
        transportation_allowance = payroll_data.get("transportation_allowance", self.ledger.loc[payroll_idx[0], "transportation_allowance"])
        other_allowances = payroll_data.get("other_allowances", self.ledger.loc[payroll_idx[0], "other_allowances"])
        
        gross_pay = base_salary + overtime_pay + bonus + meal_allowance + transportation_allowance + other_allowances
        
        # 공제액 계산
        income_tax = payroll_data.get("income_tax", gross_pay * 0.03)  # 소득세 (기본 3%)
        local_income_tax = payroll_data.get("local_income_tax", income_tax * 0.1)  # 지방소득세 (소득세의 10%)
        national_pension = payroll_data.get("national_pension", gross_pay * 0.045)  # 국민연금 (4.5%)
        health_insurance = payroll_data.get("health_insurance", gross_pay * 0.0343)  # 건강보험 (3.43%)
        employment_insurance = payroll_data.get("employment_insurance", gross_pay * 0.008)  # 고용보험 (0.8%)
        
        total_deductions = income_tax + local_income_tax + national_pension + health_insurance + employment_insurance
        
        # 실수령액 계산
        net_pay = gross_pay - total_deductions
        
        # 임금 지급 정보 업데이트
        update_data = {
            "payment_date": payroll_data.get("payment_date", self.ledger.loc[payroll_idx[0], "payment_date"]),
            "payment_period_start": payroll_data.get("payment_period_start", self.ledger.loc[payroll_idx[0], "payment_period_start"]),
            "payment_period_end": payroll_data.get("payment_period_end", self.ledger.loc[payroll_idx[0], "payment_period_end"]),
            "base_salary": base_salary,
            "overtime_hours": payroll_data.get("overtime_hours", self.ledger.loc[payroll_idx[0], "overtime_hours"]),
            "overtime_pay": overtime_pay,
            "bonus": bonus,
            "meal_allowance": meal_allowance,
            "transportation_allowance": transportation_allowance,
            "other_allowances": other_allowances,
            "gross_pay": gross_pay,
            "income_tax": income_tax,
            "local_income_tax": local_income_tax,
            "national_pension": national_pension,
            "health_insurance": health_insurance,
            "employment_insurance": employment_insurance,
            "total_deductions": total_deductions,
            "net_pay": net_pay,
            "payment_method": payroll_data.get("payment_method", self.ledger.loc[payroll_idx[0], "payment_method"]),
            "note": payroll_data.get("note", self.ledger.loc[payroll_idx[0], "note"])
        }
        
        # 임금 지급 정보 업데이트
        for key, value in update_data.items():
            self.ledger.loc[payroll_idx, key] = value
        
        # 데이터 저장
        self.save_data()
        
        return True
    
    def delete_payroll(self, ledger_id):
        """
        임금 지급 기록 삭제
        
        Args:
            ledger_id (str): 임금 지급 ID
            
        Returns:
            bool: 삭제 성공 여부
        """
        # 임금 지급 정보 찾기
        payroll_idx = self.ledger[self.ledger["ledger_id"] == ledger_id].index
        
        if len(payroll_idx) == 0:
            return False
        
        # 임금 지급 정보 삭제
        self.ledger = self.ledger.drop(payroll_idx)
        
        # 데이터 저장
        self.save_data()
        
        return True
    
    def get_payroll(self, ledger_id):
        """
        임금 지급 기록 조회
        
        Args:
            ledger_id (str): 임금 지급 ID
            
        Returns:
            dict: 임금 지급 정보
        """
        payroll = self.ledger[self.ledger["ledger_id"] == ledger_id]
        
        if len(payroll) == 0:
            return None
        
        return payroll.iloc[0].to_dict()
    
    def get_employee_payrolls(self, employee_id):
        """
        직원별 임금 지급 기록 조회
        
        Args:
            employee_id (str): 직원 ID
            
        Returns:
            pandas.DataFrame: 직원별 임금 지급 기록
        """
        return self.ledger[self.ledger["employee_id"] == employee_id].sort_values("payment_date", ascending=False)
    
    def get_payrolls_by_period(self, start_date, end_date):
        """
        기간별 임금 지급 기록 조회
        
        Args:
            start_date (str): 시작일 (YYYY-MM-DD 형식)
            end_date (str): 종료일 (YYYY-MM-DD 형식)
            
        Returns:
            pandas.DataFrame: 기간별 임금 지급 기록
        """
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date)
        
        return self.ledger[
            (self.ledger["payment_date"] >= start_date) & 
            (self.ledger["payment_date"] <= end_date)
        ].sort_values("payment_date", ascending=False)
    
    def get_all_payrolls(self):
        """
        모든 임금 지급 기록 조회
        
        Returns:
            pandas.DataFrame: 모든 임금 지급 기록
        """
        return self.ledger.sort_values("payment_date", ascending=False)
    
    def generate_monthly_report(self, year, month):
        """
        월별 임금 지급 보고서 생성
        
        Args:
            year (int): 연도
            month (int): 월
            
        Returns:
            dict: 월별 임금 지급 보고서
        """
        # 해당 월의 시작일과 종료일
        start_date = pd.Timestamp(year=year, month=month, day=1)
        if month == 12:
            end_date = pd.Timestamp(year=year+1, month=1, day=1) - pd.Timedelta(days=1)
        else:
            end_date = pd.Timestamp(year=year, month=month+1, day=1) - pd.Timedelta(days=1)
        
        # 해당 월의 임금 지급 기록
        monthly_payrolls = self.get_payrolls_by_period(start_date, end_date)
        
        # 보고서 데이터
        report = {
            "year": year,
            "month": month,
            "total_employees": len(monthly_payrolls["employee_id"].unique()),
            "total_gross_pay": monthly_payrolls["gross_pay"].sum(),
            "total_deductions": monthly_payrolls["total_deductions"].sum(),
            "total_net_pay": monthly_payrolls["net_pay"].sum(),
            "avg_gross_pay": monthly_payrolls["gross_pay"].mean(),
            "avg_net_pay": monthly_payrolls["net_pay"].mean(),
            "detail": monthly_payrolls
        }
        
        return report
    
    def generate_annual_report(self, year):
        """
        연간 임금 지급 보고서 생성
        
        Args:
            year (int): 연도
            
        Returns:
            dict: 연간 임금 지급 보고서
        """
        # 해당 연도의 시작일과 종료일
        start_date = pd.Timestamp(year=year, month=1, day=1)
        end_date = pd.Timestamp(year=year, month=12, day=31)
        
        # 해당 연도의 임금 지급 기록
        annual_payrolls = self.get_payrolls_by_period(start_date, end_date)
        
        # 월별 통계
        monthly_stats = []
        for month in range(1, 13):
            month_start = pd.Timestamp(year=year, month=month, day=1)
            if month == 12:
                month_end = pd.Timestamp(year=year+1, month=1, day=1) - pd.Timedelta(days=1)
            else:
                month_end = pd.Timestamp(year=year, month=month+1, day=1) - pd.Timedelta(days=1)
            
            month_payrolls = self.get_payrolls_by_period(month_start, month_end)
            
            monthly_stats.append({
                "month": month,
                "total_employees": len(month_payrolls["employee_id"].unique()),
                "total_gross_pay": month_payrolls["gross_pay"].sum(),
                "total_deductions": month_payrolls["total_deductions"].sum(),
                "total_net_pay": month_payrolls["net_pay"].sum()
            })
        
        # 보고서 데이터
        report = {
            "year": year,
            "total_employees": len(annual_payrolls["employee_id"].unique()),
            "total_gross_pay": annual_payrolls["gross_pay"].sum(),
            "total_deductions": annual_payrolls["total_deductions"].sum(),
            "total_net_pay": annual_payrolls["net_pay"].sum(),
            "avg_gross_pay": annual_payrolls["gross_pay"].mean(),
            "avg_net_pay": annual_payrolls["net_pay"].mean(),
            "monthly_stats": monthly_stats,
            "detail": annual_payrolls
        }
        
        return report
    
    def export_to_excel(self, file_path, payrolls=None):
        """
        임금대장 데이터를 엑셀로 내보내기
        
        Args:
            file_path (str): 저장할 파일 경로
            payrolls (pandas.DataFrame, optional): 내보낼 임금대장 데이터. 기본값은 None.
            
        Returns:
            bool: 내보내기 성공 여부
        """
        import xlsxwriter
        
        # 내보낼 데이터 설정
        if payrolls is None:
            payrolls = self.get_all_payrolls()
        
        # 직원 정보 조회
        employee_dict = {}
        for _, employee in self.employees.iterrows():
            employee_dict[employee["employee_id"]] = employee["name"]
        
        # 직원 이름 열 추가
        payrolls_with_name = payrolls.copy()
        payrolls_with_name["employee_name"] = payrolls_with_name["employee_id"].map(employee_dict)
        
        # 필요한 열 선택 및 정렬
        columns = [
            "ledger_id", "employee_id", "employee_name", "payment_date",
            "payment_period_start", "payment_period_end", "base_salary",
            "overtime_hours", "overtime_pay", "bonus", "meal_allowance",
            "transportation_allowance", "other_allowances", "gross_pay",
            "income_tax", "local_income_tax", "national_pension",
            "health_insurance", "employment_insurance", "total_deductions",
            "net_pay", "payment_method", "note"
        ]
        
        # 열 이름 매핑
        column_mapping = {
            "ledger_id": "지급 ID",
            "employee_id": "직원 ID",
            "employee_name": "직원 이름",
            "payment_date": "지급일",
            "payment_period_start": "지급 기간 시작",
            "payment_period_end": "지급 기간 종료",
            "base_salary": "기본급",
            "overtime_hours": "초과근무 시간",
            "overtime_pay": "초과근무 수당",
            "bonus": "상여금",
            "meal_allowance": "식대",
            "transportation_allowance": "교통비",
            "other_allowances": "기타 수당",
            "gross_pay": "총 지급액",
            "income_tax": "소득세",
            "local_income_tax": "지방소득세",
            "national_pension": "국민연금",
            "health_insurance": "건강보험",
            "employment_insurance": "고용보험",
            "total_deductions": "총 공제액",
            "net_pay": "실수령액",
            "payment_method": "지급 방법",
            "note": "비고"
        }
        
        # 데이터 프레임 변환
        export_df = payrolls_with_name[columns].rename(columns=column_mapping)
        
        try:
            # 엑셀 파일로 저장
            export_df.to_excel(file_path, index=False, engine="xlsxwriter")
            return True
        except Exception as e:
            print(f"엑셀 내보내기 오류: {e}")
            return False

def render_payroll_ledger_ui():
    """
    임금대장 UI 렌더링 함수
    """
    st.title("💰 임금대장 관리")
    
    # 임금대장 인스턴스 생성
    ledger = PayrollLedger()
    
    # 탭 생성
    tabs = st.tabs(["직원 관리", "임금 지급 관리", "보고서"])
    
    # 직원 관리 탭
    with tabs[0]:
        st.header("직원 관리")
        
        # 직원 목록
        employees = ledger.get_all_employees()
        
        if not employees.empty:
            # 직원 정보 표시
            st.subheader("직원 목록")
            
            # 테이블 열 이름 변경
            display_employees = employees.copy()
            display_employees = display_employees.rename(columns={
                "employee_id": "직원 ID",
                "name": "이름",
                "department": "부서",
                "position": "직급",
                "entry_date": "입사일",
                "base_salary": "기본급",
                "hourly_rate": "시급",
                "payment_type": "급여 유형"
            })
            
            st.dataframe(display_employees, use_container_width=True)
            
            # 직원 상세 정보
            st.subheader("직원 상세 정보")
            
            # 직원 선택
            employee_ids = employees["employee_id"].tolist()
            employee_names = employees["name"].tolist()
            
            # 직원 ID와 이름 함께 표시
            employee_options = [f"{name} (ID: {emp_id})" for name, emp_id in zip(employee_names, employee_ids)]
            
            selected_employee = st.selectbox("직원 선택", employee_options)
            selected_employee_id = selected_employee.split("(ID: ")[1].split(")")[0]
            
            # 선택한 직원 정보 표시
            employee = ledger.get_employee(selected_employee_id)
            
            if employee:
                with st.form("employee_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        name = st.text_input("이름", value=employee["name"])
                        department = st.text_input("부서", value=employee["department"])
                        position = st.text_input("직급", value=employee["position"])
                    
                    with col2:
                        entry_date = st.date_input(
                            "입사일",
                            value=pd.to_datetime(employee["entry_date"]).date() if pd.notna(employee["entry_date"]) else datetime.date.today(),
                            format="YYYY-MM-DD"
                        )
                        payment_type = st.selectbox(
                            "급여 유형",
                            options=["monthly", "hourly"],
                            index=0 if employee["payment_type"] == "monthly" else 1
                        )
                    
                    if payment_type == "monthly":
                        base_salary = st.number_input("기본급 (원)", value=int(employee["base_salary"]), step=100000)
                        hourly_rate = 0
                    else:
                        hourly_rate = st.number_input("시급 (원)", value=int(employee["hourly_rate"]), step=1000)
                        base_salary = 0
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        update_button = st.form_submit_button("직원 정보 수정")
                    
                    with col2:
                        delete_button = st.form_submit_button("직원 삭제", type="secondary")
                    
                    with col3:
                        pass
                
                # 직원 정보 업데이트
                if update_button:
                    employee_data = {
                        "name": name,
                        "department": department,
                        "position": position,
                        "entry_date": entry_date.strftime("%Y-%m-%d"),
                        "payment_type": payment_type,
                        "base_salary": base_salary,
                        "hourly_rate": hourly_rate
                    }
                    
                    if ledger.update_employee(selected_employee_id, employee_data):
                        st.success("직원 정보가 업데이트되었습니다.")
                        st.rerun()
                    else:
                        st.error("직원 정보 업데이트에 실패했습니다.")
                
                # 직원 삭제
                if delete_button:
                    if ledger.delete_employee(selected_employee_id):
                        st.success("직원이 삭제되었습니다.")
                        st.rerun()
                    else:
                        st.error("직원 삭제에 실패했습니다.")
        
        # 새 직원 추가
        st.subheader("새 직원 추가")
        
        with st.form("new_employee_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("이름")
                department = st.text_input("부서")
                position = st.text_input("직급")
            
            with col2:
                entry_date = st.date_input("입사일", value=datetime.date.today(), format="YYYY-MM-DD")
                payment_type = st.selectbox("급여 유형", options=["monthly", "hourly"])
            
            if payment_type == "monthly":
                base_salary = st.number_input("기본급 (원)", value=3000000, step=100000)
                hourly_rate = 0
            else:
                hourly_rate = st.number_input("시급 (원)", value=9620, step=1000)
                base_salary = 0
            
            submit_button = st.form_submit_button("직원 등록")
        
        if submit_button:
            employee_data = {
                "name": name,
                "department": department,
                "position": position,
                "entry_date": entry_date.strftime("%Y-%m-%d"),
                "payment_type": payment_type,
                "base_salary": base_salary,
                "hourly_rate": hourly_rate
            }
            
            employee_id = ledger.add_employee(employee_data)
            
            if employee_id:
                st.success(f"직원이 등록되었습니다. (ID: {employee_id})")
                st.rerun()
            else:
                st.error("직원 등록에 실패했습니다.")
    
    # 임금 지급 관리 탭
    with tabs[1]:
        st.header("임금 지급 관리")
        
        # 임금 지급 기록 목록
        payrolls = ledger.get_all_payrolls()
        
        if not payrolls.empty:
            # 임금 지급 기록 표시
            st.subheader("임금 지급 기록")
            
            # 직원 이름 매핑
            employees = ledger.get_all_employees()
            employee_dict = {}
            for _, employee in employees.iterrows():
                employee_dict[employee["employee_id"]] = employee["name"]
            
            # 임금 지급 기록에 직원 이름 추가
            payrolls_with_name = payrolls.copy()
            payrolls_with_name["employee_name"] = payrolls_with_name["employee_id"].map(employee_dict)
            
            # 테이블 열 이름 변경
            display_columns = ["ledger_id", "employee_name", "payment_date", "gross_pay", "total_deductions", "net_pay"]
            display_column_names = {
                "ledger_id": "지급 ID",
                "employee_name": "직원 이름",
                "payment_date": "지급일",
                "gross_pay": "총 지급액",
                "total_deductions": "총 공제액",
                "net_pay": "실수령액"
            }
            
            display_payrolls = payrolls_with_name[display_columns].rename(columns=display_column_names)
            
            st.dataframe(display_payrolls, use_container_width=True)
            
            # 임금 지급 기록 상세 정보
            st.subheader("임금 지급 상세 정보")
            
            # 임금 지급 기록 선택
            ledger_ids = payrolls["ledger_id"].tolist()
            payroll_options = []
            
            for _, row in payrolls_with_name.iterrows():
                payment_date = pd.to_datetime(row["payment_date"]).strftime("%Y-%m-%d")
                payroll_options.append(f"{row['employee_name']} - {payment_date} (ID: {row['ledger_id']})")
            
            selected_payroll = st.selectbox("임금 지급 기록 선택", payroll_options)
            selected_ledger_id = selected_payroll.split("(ID: ")[1].split(")")[0]
            
            # 선택한 임금 지급 기록 표시
            payroll = ledger.get_payroll(selected_ledger_id)
            
            if payroll:
                employee = ledger.get_employee(payroll["employee_id"])
                
                with st.form("payroll_form"):
                    st.subheader(f"{employee['name']}의 임금 지급 정보")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        payment_date = st.date_input(
                            "지급일",
                            value=pd.to_datetime(payroll["payment_date"]).date(),
                            format="YYYY-MM-DD"
                        )
                    
                    with col2:
                        payment_period_start = st.date_input(
                            "지급 기간 시작",
                            value=pd.to_datetime(payroll["payment_period_start"]).date() if pd.notna(payroll["payment_period_start"]) else pd.to_datetime(payroll["payment_date"]).date() - datetime.timedelta(days=30),
                            format="YYYY-MM-DD"
                        )
                    
                    with col3:
                        payment_period_end = st.date_input(
                            "지급 기간 종료",
                            value=pd.to_datetime(payroll["payment_period_end"]).date() if pd.notna(payroll["payment_period_end"]) else pd.to_datetime(payroll["payment_date"]).date(),
                            format="YYYY-MM-DD"
                        )
                    
                    st.subheader("지급 내역")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        base_salary = st.number_input("기본급", value=int(payroll["base_salary"]), step=10000)
                        overtime_hours = st.number_input("초과근무 시간", value=float(payroll["overtime_hours"]), step=0.5)
                        overtime_pay = st.number_input("초과근무 수당", value=int(payroll["overtime_pay"]), step=10000)
                    
                    with col2:
                        bonus = st.number_input("상여금", value=int(payroll["bonus"]), step=10000)
                        meal_allowance = st.number_input("식대", value=int(payroll["meal_allowance"]), step=10000)
                        transportation_allowance = st.number_input("교통비", value=int(payroll["transportation_allowance"]), step=10000)
                        other_allowances = st.number_input("기타 수당", value=int(payroll["other_allowances"]), step=10000)
                    
                    st.subheader("공제 내역")
                    
                    # 총 지급액 계산
                    gross_pay = base_salary + overtime_pay + bonus + meal_allowance + transportation_allowance + other_allowances
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        income_tax = st.number_input("소득세", value=float(payroll["income_tax"]), step=1000.0, format="%.2f")
                        local_income_tax = st.number_input("지방소득세", value=float(payroll["local_income_tax"]), step=100.0, format="%.2f")
                        national_pension = st.number_input("국민연금", value=float(payroll["national_pension"]), step=1000.0, format="%.2f")
                    
                    with col2:
                        health_insurance = st.number_input("건강보험", value=float(payroll["health_insurance"]), step=1000.0, format="%.2f")
                        employment_insurance = st.number_input("고용보험", value=float(payroll["employment_insurance"]), step=1000.0, format="%.2f")
                    
                    # 총 공제액 및 실수령액 계산
                    total_deductions = income_tax + local_income_tax + national_pension + health_insurance + employment_insurance
                    net_pay = gross_pay - total_deductions
                    
                    st.subheader("최종 금액")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("총 지급액", f"{gross_pay:,.0f}원")
                    
                    with col2:
                        st.metric("총 공제액", f"{total_deductions:,.2f}원")
                    
                    with col3:
                        st.metric("실수령액", f"{net_pay:,.2f}원")
                    
                    st.subheader("기타 정보")
                    
                    payment_method = st.selectbox(
                        "지급 방법",
                        options=["계좌이체", "현금", "수표", "기타"],
                        index=["계좌이체", "현금", "수표", "기타"].index(payroll["payment_method"]) if payroll["payment_method"] in ["계좌이체", "현금", "수표", "기타"] else 0
                    )
                    
                    note = st.text_area("비고", value=payroll["note"] if pd.notna(payroll["note"]) else "")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        update_button = st.form_submit_button("임금 지급 정보 수정")
                    
                    with col2:
                        delete_button = st.form_submit_button("임금 지급 기록 삭제", type="secondary")
                    
                    with col3:
                        pass
                
                # 임금 지급 정보 업데이트
                if update_button:
                    payroll_data = {
                        "payment_date": payment_date.strftime("%Y-%m-%d"),
                        "payment_period_start": payment_period_start.strftime("%Y-%m-%d"),
                        "payment_period_end": payment_period_end.strftime("%Y-%m-%d"),
                        "base_salary": base_salary,
                        "overtime_hours": overtime_hours,
                        "overtime_pay": overtime_pay,
                        "bonus": bonus,
                        "meal_allowance": meal_allowance,
                        "transportation_allowance": transportation_allowance,
                        "other_allowances": other_allowances,
                        "income_tax": income_tax,
                        "local_income_tax": local_income_tax,
                        "national_pension": national_pension,
                        "health_insurance": health_insurance,
                        "employment_insurance": employment_insurance,
                        "payment_method": payment_method,
                        "note": note
                    }
                    
                    if ledger.update_payroll(selected_ledger_id, payroll_data):
                        st.success("임금 지급 정보가 업데이트되었습니다.")
                        st.rerun()
                    else:
                        st.error("임금 지급 정보 업데이트에 실패했습니다.")
                
                # 임금 지급 기록 삭제
                if delete_button:
                    if ledger.delete_payroll(selected_ledger_id):
                        st.success("임금 지급 기록이 삭제되었습니다.")
                        st.rerun()
                    else:
                        st.error("임금 지급 기록 삭제에 실패했습니다.")
        
        # 새 임금 지급 기록 추가
        st.subheader("새 임금 지급 기록 추가")
        
        # 직원 목록
        employees = ledger.get_all_employees()
        
        if not employees.empty:
            with st.form("new_payroll_form"):
                # 직원 선택
                employee_ids = employees["employee_id"].tolist()
                employee_names = employees["name"].tolist()
                employee_options = [f"{name} (ID: {emp_id})" for name, emp_id in zip(employee_names, employee_ids)]
                
                selected_employee = st.selectbox("직원 선택", employee_options, key="new_payroll_employee")
                selected_employee_id = selected_employee.split("(ID: ")[1].split(")")[0]
                
                # 선택한 직원 정보
                employee = ledger.get_employee(selected_employee_id)
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    payment_date = st.date_input("지급일", value=datetime.date.today(), format="YYYY-MM-DD")
                
                with col2:
                    payment_period_start = st.date_input("지급 기간 시작", value=datetime.date.today() - datetime.timedelta(days=30), format="YYYY-MM-DD")
                
                with col3:
                    payment_period_end = st.date_input("지급 기간 종료", value=datetime.date.today(), format="YYYY-MM-DD")
                
                st.subheader("지급 내역")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    base_salary = st.number_input("기본급", value=int(employee["base_salary"]), step=10000, key="new_base_salary")
                    overtime_hours = st.number_input("초과근무 시간", value=0.0, step=0.5, key="new_overtime_hours")
                    overtime_pay = st.number_input("초과근무 수당", value=0, step=10000, key="new_overtime_pay")
                
                with col2:
                    bonus = st.number_input("상여금", value=0, step=10000, key="new_bonus")
                    meal_allowance = st.number_input("식대", value=100000, step=10000, key="new_meal_allowance")
                    transportation_allowance = st.number_input("교통비", value=50000, step=10000, key="new_transportation_allowance")
                    other_allowances = st.number_input("기타 수당", value=0, step=10000, key="new_other_allowances")
                
                st.subheader("공제 내역")
                
                # 총 지급액 계산
                gross_pay = base_salary + overtime_pay + bonus + meal_allowance + transportation_allowance + other_allowances
                
                # 공제액 자동 계산
                income_tax = gross_pay * 0.03  # 소득세 (기본 3%)
                local_income_tax = income_tax * 0.1  # 지방소득세 (소득세의 10%)
                national_pension = gross_pay * 0.045  # 국민연금 (4.5%)
                health_insurance = gross_pay * 0.0343  # 건강보험 (3.43%)
                employment_insurance = gross_pay * 0.008  # 고용보험 (0.8%)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    income_tax = st.number_input("소득세", value=income_tax, step=1000.0, format="%.2f", key="new_income_tax")
                    local_income_tax = st.number_input("지방소득세", value=local_income_tax, step=100.0, format="%.2f", key="new_local_income_tax")
                    national_pension = st.number_input("국민연금", value=national_pension, step=1000.0, format="%.2f", key="new_national_pension")
                
                with col2:
                    health_insurance = st.number_input("건강보험", value=health_insurance, step=1000.0, format="%.2f", key="new_health_insurance")
                    employment_insurance = st.number_input("고용보험", value=employment_insurance, step=1000.0, format="%.2f", key="new_employment_insurance")
                
                # 총 공제액 및 실수령액 계산
                total_deductions = income_tax + local_income_tax + national_pension + health_insurance + employment_insurance
                net_pay = gross_pay - total_deductions
                
                st.subheader("최종 금액")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("총 지급액", f"{gross_pay:,.0f}원")
                
                with col2:
                    st.metric("총 공제액", f"{total_deductions:,.2f}원")
                
                with col3:
                    st.metric("실수령액", f"{net_pay:,.2f}원")
                
                st.subheader("기타 정보")
                
                payment_method = st.selectbox(
                    "지급 방법",
                    options=["계좌이체", "현금", "수표", "기타"],
                    index=0,
                    key="new_payment_method"
                )
                
                note = st.text_area("비고", value="", key="new_note")
                
                submit_button = st.form_submit_button("임금 지급 기록 추가")
            
            if submit_button:
                payroll_data = {
                    "employee_id": selected_employee_id,
                    "payment_date": payment_date.strftime("%Y-%m-%d"),
                    "payment_period_start": payment_period_start.strftime("%Y-%m-%d"),
                    "payment_period_end": payment_period_end.strftime("%Y-%m-%d"),
                    "base_salary": base_salary,
                    "overtime_hours": overtime_hours,
                    "overtime_pay": overtime_pay,
                    "bonus": bonus,
                    "meal_allowance": meal_allowance,
                    "transportation_allowance": transportation_allowance,
                    "other_allowances": other_allowances,
                    "income_tax": income_tax,
                    "local_income_tax": local_income_tax,
                    "national_pension": national_pension,
                    "health_insurance": health_insurance,
                    "employment_insurance": employment_insurance,
                    "payment_method": payment_method,
                    "note": note
                }
                
                ledger_id = ledger.add_payroll(payroll_data)
                
                if ledger_id:
                    st.success(f"임금 지급 기록이 추가되었습니다. (ID: {ledger_id})")
                    st.rerun()
                else:
                    st.error("임금 지급 기록 추가에 실패했습니다.")
        else:
            st.warning("직원이 등록되어 있지 않습니다. 먼저 직원을 등록해주세요.")
    
    # 보고서 탭
    with tabs[2]:
        st.header("보고서")
        
        # 보고서 유형 선택
        report_type = st.radio("보고서 유형", ["월별 보고서", "연간 보고서"])
        
        if report_type == "월별 보고서":
            # 연도 및 월 선택
            col1, col2 = st.columns(2)
            
            with col1:
                current_year = datetime.date.today().year
                year = st.selectbox("연도", list(range(current_year - 5, current_year + 1)), index=5)
            
            with col2:
                current_month = datetime.date.today().month
                month = st.selectbox("월", list(range(1, 13)), index=current_month - 1)
            
            if st.button("보고서 생성"):
                # 월별 보고서 생성
                report = ledger.generate_monthly_report(year, month)
                
                if len(report["detail"]) > 0:
                    # 요약 정보
                    st.subheader(f"{year}년 {month}월 임금 지급 요약")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("총 직원 수", f"{report['total_employees']}명")
                    
                    with col2:
                        st.metric("총 지급액", f"{report['total_gross_pay']:,.0f}원")
                    
                    with col3:
                        st.metric("총 실수령액", f"{report['total_net_pay']:,.0f}원")
                    
                    # 직원별 통계
                    st.subheader("직원별 통계")
                    
                    # 직원 이름 매핑
                    employees = ledger.get_all_employees()
                    employee_dict = {}
                    for _, employee in employees.iterrows():
                        employee_dict[employee["employee_id"]] = employee["name"]
                    
                    # 직원별 통계 데이터
                    employee_stats = report["detail"].groupby("employee_id").agg({
                        "gross_pay": "sum",
                        "total_deductions": "sum",
                        "net_pay": "sum"
                    }).reset_index()
                    
                    employee_stats["employee_name"] = employee_stats["employee_id"].map(employee_dict)
                    
                    # 테이블 열 이름 변경
                    display_columns = ["employee_name", "gross_pay", "total_deductions", "net_pay"]
                    display_column_names = {
                        "employee_name": "직원 이름",
                        "gross_pay": "총 지급액",
                        "total_deductions": "총 공제액",
                        "net_pay": "실수령액"
                    }
                    
                    display_stats = employee_stats[display_columns].rename(columns=display_column_names)
                    
                    st.dataframe(display_stats, use_container_width=True)
                    
                    # 금액 분포 시각화
                    st.subheader("금액 분포")
                    
                    fig = px.bar(
                        employee_stats,
                        x="employee_name",
                        y=["gross_pay", "net_pay"],
                        title=f"{year}년 {month}월 직원별 급여 분포",
                        labels={
                            "employee_name": "직원 이름",
                            "value": "금액 (원)",
                            "variable": "구분"
                        },
                        barmode="group",
                        color_discrete_map={
                            "gross_pay": "#1E88E5",
                            "net_pay": "#4CAF50"
                        }
                    )
                    
                    fig.update_layout(
                        xaxis_title="직원",
                        yaxis_title="금액 (원)",
                        legend_title="구분",
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 공제 내역 시각화
                    st.subheader("공제 내역")
                    
                    # 공제 항목별 합계
                    deduction_data = {
                        "항목": ["소득세", "지방소득세", "국민연금", "건강보험", "고용보험"],
                        "금액": [
                            report["detail"]["income_tax"].sum(),
                            report["detail"]["local_income_tax"].sum(),
                            report["detail"]["national_pension"].sum(),
                            report["detail"]["health_insurance"].sum(),
                            report["detail"]["employment_insurance"].sum()
                        ]
                    }
                    
                    deduction_df = pd.DataFrame(deduction_data)
                    
                    fig = px.pie(
                        deduction_df,
                        values="금액",
                        names="항목",
                        title=f"{year}년 {month}월 공제 내역 분포",
                        color_discrete_sequence=px.colors.sequential.Blues_r
                    )
                    
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 엑셀 파일 내보내기
                    st.subheader("보고서 다운로드")
                    
                    if st.button("엑셀 파일로 내보내기"):
                        # 임시 파일 경로
                        temp_file = os.path.join(ledger.data_dir, f"monthly_report_{year}_{month}.xlsx")
                        
                        # 엑셀 파일로 저장
                        if ledger.export_to_excel(temp_file, report["detail"]):
                            # 파일 읽기
                            with open(temp_file, "rb") as file:
                                file_data = file.read()
                            
                            # 다운로드 링크 생성
                            b64 = base64.b64encode(file_data).decode()
                            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="monthly_report_{year}_{month}.xlsx">엑셀 파일 다운로드</a>'
                            
                            st.markdown(href, unsafe_allow_html=True)
                        else:
                            st.error("엑셀 파일 내보내기에 실패했습니다.")
                else:
                    st.warning(f"{year}년 {month}월에 임금 지급 기록이 없습니다.")
        else:  # 연간 보고서
            # 연도 선택
            current_year = datetime.date.today().year
            year = st.selectbox("연도", list(range(current_year - 5, current_year + 1)), index=5)
            
            if st.button("보고서 생성"):
                # 연간 보고서 생성
                report = ledger.generate_annual_report(year)
                
                if len(report["detail"]) > 0:
                    # 요약 정보
                    st.subheader(f"{year}년 임금 지급 요약")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("총 직원 수", f"{report['total_employees']}명")
                    
                    with col2:
                        st.metric("총 지급액", f"{report['total_gross_pay']:,.0f}원")
                    
                    with col3:
                        st.metric("총 실수령액", f"{report['total_net_pay']:,.0f}원")
                    
                    # 월별 통계
                    st.subheader("월별 통계")
                    
                    # 월별 통계 데이터
                    monthly_stats = pd.DataFrame(report["monthly_stats"])
                    
                    # 테이블 열 이름 변경
                    display_columns = ["month", "total_employees", "total_gross_pay", "total_deductions", "total_net_pay"]
                    display_column_names = {
                        "month": "월",
                        "total_employees": "직원 수",
                        "total_gross_pay": "총 지급액",
                        "total_deductions": "총 공제액",
                        "total_net_pay": "총 실수령액"
                    }
                    
                    display_stats = monthly_stats[display_columns].rename(columns=display_column_names)
                    
                    st.dataframe(display_stats, use_container_width=True)
                    
                    # 월별 급여 추이 시각화
                    st.subheader("월별 급여 추이")
                    
                    fig = px.line(
                        monthly_stats,
                        x="month",
                        y=["total_gross_pay", "total_net_pay"],
                        title=f"{year}년 월별 급여 추이",
                        labels={
                            "month": "월",
                            "value": "금액 (원)",
                            "variable": "구분"
                        },
                        markers=True,
                        color_discrete_map={
                            "total_gross_pay": "#1E88E5",
                            "total_net_pay": "#4CAF50"
                        }
                    )
                    
                    fig.update_layout(
                        xaxis_title="월",
                        yaxis_title="금액 (원)",
                        legend_title="구분",
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 직원별 통계
                    st.subheader("직원별 통계")
                    
                    # 직원 이름 매핑
                    employees = ledger.get_all_employees()
                    employee_dict = {}
                    for _, employee in employees.iterrows():
                        employee_dict[employee["employee_id"]] = employee["name"]
                    
                    # 직원별 통계 데이터
                    employee_stats = report["detail"].groupby("employee_id").agg({
                        "gross_pay": "sum",
                        "total_deductions": "sum",
                        "net_pay": "sum"
                    }).reset_index()
                    
                    employee_stats["employee_name"] = employee_stats["employee_id"].map(employee_dict)
                    
                    # 테이블 열 이름 변경
                    display_columns = ["employee_name", "gross_pay", "total_deductions", "net_pay"]
                    display_column_names = {
                        "employee_name": "직원 이름",
                        "gross_pay": "총 지급액",
                        "total_deductions": "총 공제액",
                        "net_pay": "실수령액"
                    }
                    
                    display_stats = employee_stats[display_columns].rename(columns=display_column_names)
                    
                    st.dataframe(display_stats, use_container_width=True)
                    
                    # 직원별 급여 분포 시각화
                    st.subheader("직원별 급여 분포")
                    
                    fig = px.bar(
                        employee_stats,
                        x="employee_name",
                        y=["gross_pay", "net_pay"],
                        title=f"{year}년 직원별 급여 분포",
                        labels={
                            "employee_name": "직원 이름",
                            "value": "금액 (원)",
                            "variable": "구분"
                        },
                        barmode="group",
                        color_discrete_map={
                            "gross_pay": "#1E88E5",
                            "net_pay": "#4CAF50"
                        }
                    )
                    
                    fig.update_layout(
                        xaxis_title="직원",
                        yaxis_title="금액 (원)",
                        legend_title="구분",
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 엑셀 파일 내보내기
                    st.subheader("보고서 다운로드")
                    
                    if st.button("엑셀 파일로 내보내기"):
                        # 임시 파일 경로
                        temp_file = os.path.join(ledger.data_dir, f"annual_report_{year}.xlsx")
                        
                        # 엑셀 파일로 저장
                        if ledger.export_to_excel(temp_file, report["detail"]):
                            # 파일 읽기
                            with open(temp_file, "rb") as file:
                                file_data = file.read()
                            
                            # 다운로드 링크 생성
                            b64 = base64.b64encode(file_data).decode()
                            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="annual_report_{year}.xlsx">엑셀 파일 다운로드</a>'
                            
                            st.markdown(href, unsafe_allow_html=True)
                        else:
                            st.error("엑셀 파일 내보내기에 실패했습니다.")
                else:
                    st.warning(f"{year}년에 임금 지급 기록이 없습니다.")

if __name__ == "__main__":
    render_payroll_ledger_ui()
