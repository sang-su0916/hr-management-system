import datetime
import pandas as pd
import numpy as np
import calendar

class AnnualLeaveCalculator:
    """
    연차휴가 계산기 클래스
    
    한국 근로기준법에 따른 연차휴가 계산 로직을 구현합니다.
    - 입사일 기준: 개인별 입사일을 기준으로 연차휴가 계산
    - 회계연도 기준: 회사의 회계연도(보통 1월 1일 ~ 12월 31일)를 기준으로 연차휴가 계산
    """
    
    def __init__(self):
        self.today = datetime.date.today()
    
    def calculate_by_entry_date(self, entry_date, target_date=None):
        """
        입사일 기준 연차휴가 계산
        
        Args:
            entry_date (str): 입사일 (YYYY-MM-DD 형식)
            target_date (str, optional): 기준일 (YYYY-MM-DD 형식). 기본값은 오늘.
            
        Returns:
            dict: 연차휴가 정보 (발생 연차, 사용 가능 연차, 다음 발생일 등)
        """
        if isinstance(entry_date, str):
            entry_date = datetime.datetime.strptime(entry_date, "%Y-%m-%d").date()
        
        if target_date is None:
            target_date = self.today
        elif isinstance(target_date, str):
            target_date = datetime.datetime.strptime(target_date, "%Y-%m-%d").date()
        
        # 근속 기간 계산 (년, 월, 일)
        years_worked, months_worked, days_worked = self._calculate_tenure(entry_date, target_date)
        
        # 근속 개월 수 계산
        total_months = years_worked * 12 + months_worked
        if days_worked > 0:
            total_months += 1
        
        # 연차휴가 계산
        annual_leave = self._calculate_annual_leave_days(entry_date, target_date, years_worked, total_months)
        
        # 다음 연차 발생일 계산
        next_annual_leave_date = self._calculate_next_annual_leave_date(entry_date, target_date)
        
        # 결과 반환
        result = {
            "entry_date": entry_date.strftime("%Y-%m-%d"),
            "target_date": target_date.strftime("%Y-%m-%d"),
            "years_worked": years_worked,
            "months_worked": total_months,
            "annual_leave_days": annual_leave,
            "next_annual_leave_date": next_annual_leave_date.strftime("%Y-%m-%d")
        }
        
        return result
    
    def calculate_by_fiscal_year(self, entry_date, fiscal_year_start=None, fiscal_year_end=None):
        """
        회계연도 기준 연차휴가 계산
        
        Args:
            entry_date (str): 입사일 (YYYY-MM-DD 형식)
            fiscal_year_start (str, optional): 회계연도 시작일 (MM-DD 형식). 기본값은 01-01.
            fiscal_year_end (str, optional): 회계연도 종료일 (MM-DD 형식). 기본값은 12-31.
            
        Returns:
            dict: 회계연도별 연차휴가 정보
        """
        if isinstance(entry_date, str):
            entry_date = datetime.datetime.strptime(entry_date, "%Y-%m-%d").date()
        
        # 회계연도 설정 (기본값: 1월 1일 ~ 12월 31일)
        if fiscal_year_start is None:
            fiscal_year_start = "01-01"
        if fiscal_year_end is None:
            fiscal_year_end = "12-31"
        
        # 현재 회계연도 계산
        current_year = self.today.year
        fy_start = datetime.datetime.strptime(f"{current_year}-{fiscal_year_start}", "%Y-%m-%d").date()
        fy_end = datetime.datetime.strptime(f"{current_year}-{fiscal_year_end}", "%Y-%m-%d").date()
        
        if self.today < fy_start:
            fy_start = datetime.datetime.strptime(f"{current_year-1}-{fiscal_year_start}", "%Y-%m-%d").date()
            fy_end = datetime.datetime.strptime(f"{current_year-1}-{fiscal_year_end}", "%Y-%m-%d").date()
        elif self.today > fy_end:
            fy_start = datetime.datetime.strptime(f"{current_year+1}-{fiscal_year_start}", "%Y-%m-%d").date()
            fy_end = datetime.datetime.strptime(f"{current_year+1}-{fiscal_year_end}", "%Y-%m-%d").date()
        
        # 입사일부터 현재까지의 회계연도별 연차휴가 계산
        fiscal_years = []
        start_year = entry_date.year
        end_year = self.today.year + 1  # 다음 해까지 계산
        
        for year in range(start_year, end_year + 1):
            fy_start_date = datetime.datetime.strptime(f"{year}-{fiscal_year_start}", "%Y-%m-%d").date()
            fy_end_date = datetime.datetime.strptime(f"{year}-{fiscal_year_end}", "%Y-%m-%d").date()
            
            # 입사일이 해당 회계연도 이후인 경우 건너뛰기
            if entry_date > fy_end_date:
                continue
            
            # 회계연도 시작일이 입사일보다 이전인 경우, 입사일을 기준으로 계산
            target_date = max(fy_start_date, entry_date)
            
            # 해당 회계연도의 연차휴가 계산
            annual_leave = self.calculate_by_entry_date(entry_date, fy_end_date)
            
            fiscal_years.append({
                "fiscal_year": f"{fy_start_date.year}-{fy_end_date.year}" if fy_start_date.year != fy_end_date.year else f"{fy_start_date.year}",
                "fiscal_year_start": fy_start_date.strftime("%Y-%m-%d"),
                "fiscal_year_end": fy_end_date.strftime("%Y-%m-%d"),
                "annual_leave_days": annual_leave["annual_leave_days"]
            })
        
        return {
            "entry_date": entry_date.strftime("%Y-%m-%d"),
            "fiscal_year_start": fiscal_year_start,
            "fiscal_year_end": fiscal_year_end,
            "fiscal_years": fiscal_years
        }
    
    def _calculate_tenure(self, entry_date, target_date):
        """
        근속 기간 계산 (년, 월, 일)
        
        Args:
            entry_date (datetime.date): 입사일
            target_date (datetime.date): 기준일
            
        Returns:
            tuple: (근속 년수, 근속 월수, 근속 일수)
        """
        years = target_date.year - entry_date.year
        months = target_date.month - entry_date.month
        days = target_date.day - entry_date.day
        
        if days < 0:
            months -= 1
            last_day_of_prev_month = calendar.monthrange(target_date.year, target_date.month - 1 if target_date.month > 1 else 12)[1]
            days += last_day_of_prev_month
        
        if months < 0:
            years -= 1
            months += 12
        
        return years, months, days
    
    def _calculate_annual_leave_days(self, entry_date, target_date, years_worked, total_months):
        """
        연차휴가 일수 계산
        
        한국 근로기준법에 따른 연차휴가 계산:
        1. 1년 미만 근무: 1개월 개근 시 1일의 유급휴가 발생 (최대 11일)
        2. 1년 이상 근무: 15일의 유급휴가 발생
        3. 3년 이상 근무: 2년마다 1일씩 추가 발생 (최대 25일)
        
        Args:
            entry_date (datetime.date): 입사일
            target_date (datetime.date): 기준일
            years_worked (int): 근속 년수
            total_months (int): 총 근속 개월 수
            
        Returns:
            int: 연차휴가 일수
        """
        # 1년 미만 근무자
        if years_worked < 1:
            return min(total_months, 11)
        
        # 1년 이상 근무자
        base_days = 15
        
        # 3년 이상 근무자는 2년마다 1일씩 추가 (최대 25일)
        if years_worked >= 3:
            additional_days = min((years_worked - 1) // 2, 10)
            base_days += additional_days
        
        return base_days
    
    def _calculate_next_annual_leave_date(self, entry_date, target_date):
        """
        다음 연차 발생일 계산
        
        Args:
            entry_date (datetime.date): 입사일
            target_date (datetime.date): 기준일
            
        Returns:
            datetime.date: 다음 연차 발생일
        """
        # 1년 미만 근무자: 다음 달 1일
        if (target_date - entry_date).days < 365:
            next_month = target_date.month + 1
            next_year = target_date.year
            
            if next_month > 12:
                next_month = 1
                next_year += 1
            
            return datetime.date(next_year, next_month, 1)
        
        # 1년 이상 근무자: 다음 입사 기념일
        next_anniversary = datetime.date(target_date.year, entry_date.month, entry_date.day)
        
        if next_anniversary < target_date:
            next_anniversary = datetime.date(target_date.year + 1, entry_date.month, entry_date.day)
        
        return next_anniversary
    
    def generate_annual_leave_table(self, entry_date, years=5):
        """
        연차휴가 발생 테이블 생성
        
        Args:
            entry_date (str): 입사일 (YYYY-MM-DD 형식)
            years (int, optional): 계산할 연도 수. 기본값은 5.
            
        Returns:
            pandas.DataFrame: 연차휴가 발생 테이블
        """
        if isinstance(entry_date, str):
            entry_date = datetime.datetime.strptime(entry_date, "%Y-%m-%d").date()
        
        data = []
        
        for year in range(years):
            target_date = entry_date.replace(year=entry_date.year + year)
            if year == 0:
                # 첫 해는 월별로 계산
                for month in range(1, 13):
                    if month < entry_date.month:
                        continue
                    
                    month_end = calendar.monthrange(entry_date.year, month)[1]
                    month_date = datetime.date(entry_date.year, month, min(entry_date.day, month_end))
                    
                    result = self.calculate_by_entry_date(entry_date, month_date)
                    
                    data.append({
                        "기준일": month_date.strftime("%Y-%m-%d"),
                        "근속기간(년)": result["years_worked"],
                        "근속기간(월)": result["months_worked"],
                        "연차휴가일수": result["annual_leave_days"]
                    })
            else:
                # 이후 연도는 연 단위로 계산
                result = self.calculate_by_entry_date(entry_date, target_date)
                
                data.append({
                    "기준일": target_date.strftime("%Y-%m-%d"),
                    "근속기간(년)": result["years_worked"],
                    "근속기간(월)": result["months_worked"],
                    "연차휴가일수": result["annual_leave_days"]
                })
        
        return pd.DataFrame(data)
