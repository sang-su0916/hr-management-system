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
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
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
        <response clipped><NOTE>To save on context only part of this file has been shown to you. You should retry this tool after you have searched inside the file with `grep -n` in order to find the line numbers of what you are looking for.</NOTE>