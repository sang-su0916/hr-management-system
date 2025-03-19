# 전체 기능 테스트 스크립트
# 이 스크립트는 HR 관리 시스템의 모든 구성 요소가 올바르게 작동하는지 테스트합니다.

import os
import sys
import unittest
import pandas as pd
import datetime

# 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 각 모듈 임포트
from annual_leave.annual_leave_calculator import AnnualLeaveCalculator
from payroll_ledger.payroll_ledger import PayrollLedger
from pay_statement.pay_statement import PayStatement

class TestHRManagementSystem(unittest.TestCase):
    """HR 관리 시스템 테스트 클래스"""
    
    def setUp(self):
        """테스트 설정"""
        # 테스트 데이터 디렉토리 생성
        self.test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_data")
        os.makedirs(self.test_data_dir, exist_ok=True)
        
        # 테스트 인스턴스 생성
        self.annual_leave_calculator = AnnualLeaveCalculator()
        self.payroll_ledger = PayrollLedger(data_dir=self.test_data_dir)
        self.pay_statement = PayStatement()
    
    def test_annual_leave_calculator(self):
        """연차휴가 계산기 테스트"""
        # 입사일 기준 연차휴가 계산 테스트
        entry_date = datetime.date.today() - datetime.timedelta(days=365*2)  # 2년 전 입사
        result = self.annual_leave_calculator.calculate_by_entry_date(entry_date)
        
        # 2년 근무자는 15일의 연차휴가가 발생해야 함
        self.assertEqual(result["annual_leave_days"], 15)
        
        # 회계연도 기준 연차휴가 계산 테스트
        fiscal_result = self.annual_leave_calculator.calculate_by_fiscal_year(entry_date)
        
        # 회계연도 기준 결과에는 fiscal_years 키가 있어야 함
        self.assertIn("fiscal_years", fiscal_result)
        
        # 연차휴가 발생 테이블 생성 테스트
        table = self.annual_leave_calculator.generate_annual_leave_table(entry_date, years=3)
        
        # 테이블은 DataFrame 타입이어야 함
        self.assertIsInstance(table, pd.DataFrame)
    
    def test_payroll_ledger(self):
        """임금대장 시스템 테스트"""
        # 직원 추가 테스트
        employee_data = {
            "name": "테스트 사용자",
            "department": "개발팀",
            "position": "개발자",
            "entry_date": datetime.date.today().strftime("%Y-%m-%d"),
            "base_salary": 3000000,
            "hourly_rate": 0,
            "payment_type": "monthly"
        }
        
        employee_id = self.payroll_ledger.add_employee(employee_data)
        
        # 직원 ID가 반환되어야 함
        self.assertIsNotNone(employee_id)
        
        # 직원 정보 조회 테스트
        employee = self.payroll_ledger.get_employee(employee_id)
        
        # 조회된 직원 정보가 있어야 함
        self.assertIsNotNone(employee)
        self.assertEqual(employee["name"], "테스트 사용자")
        
        # 임금 지급 기록 추가 테스트
        payroll_data = {
            "employee_id": employee_id,
            "payment_date": datetime.date.today().strftime("%Y-%m-%d"),
            "payment_period_start": (datetime.date.today() - datetime.timedelta(days=30)).strftime("%Y-%m-%d"),
            "payment_period_end": datetime.date.today().strftime("%Y-%m-%d"),
            "base_salary": 3000000,
            "overtime_hours": 10,
            "overtime_pay": 300000,
            "bonus": 500000,
            "meal_allowance": 100000,
            "transportation_allowance": 50000,
            "other_allowances": 0
        }
        
        ledger_id = self.payroll_ledger.add_payroll(payroll_data)
        
        # 임금 지급 ID가 반환되어야 함
        self.assertIsNotNone(ledger_id)
        
        # 임금 지급 기록 조회 테스트
        payroll = self.payroll_ledger.get_payroll(ledger_id)
        
        # 조회된 임금 지급 기록이 있어야 함
        self.assertIsNotNone(payroll)
        self.assertEqual(payroll["base_salary"], 3000000)
    
    def tearDown(self):
        """테스트 정리"""
        # 테스트 데이터 파일 삭제
        if os.path.exists(os.path.join(self.test_data_dir, "employees.csv")):
            os.remove(os.path.join(self.test_data_dir, "employees.csv"))
        
        if os.path.exists(os.path.join(self.test_data_dir, "payroll_ledger.csv")):
            os.remove(os.path.join(self.test_data_dir, "payroll_ledger.csv"))
        
        # 테스트 데이터 디렉토리 삭제
        if os.path.exists(self.test_data_dir):
            os.rmdir(self.test_data_dir)

if __name__ == "__main__":
    unittest.main()
