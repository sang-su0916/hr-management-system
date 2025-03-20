import datetime
import calendar
import math
import pandas as pd
import numpy as np

class AnnualLeaveCalculator:
    """
    연차휴가 계산기 클래스
    
    한국 근로기준법에 따른 연차휴가 계산 로직을 구현합니다.
    - 입사일 기준: 개인별 입사일을 기준으로 연차휴가 계산
    - 회계연도 기준: 회사의 회계연도(보통 1월 1일 ~ 12월 31일)를 기준으로 연차휴가 계산
    """
    
    def __init__(self, hire_date, termination_date=None):
        """
        초기화
        
        Args:
            hire_date (datetime.date): 입사일
            termination_date (datetime.date, optional): 퇴사일. 기본값은 None.
        """
        self.hire_date = hire_date
        self.termination_date = termination_date
        self.today = datetime.date.today()
        
        # 퇴사일이 없으면 현재 날짜 기준으로 계산
        if self.termination_date is None:
            self.calculation_end_date = self.today + datetime.timedelta(days=365*5)  # 5년 후까지 계산
        else:
            self.calculation_end_date = self.termination_date
    
    def get_employment_year_leaves(self):
        """
        입사연도 기준 연차휴가 계산
        
        Returns:
            dict: 연도별 연차일수 (키: 연도, 값: 일수)
        """
        result = {}
        current_date = self.hire_date
        years_worked = 0
        
        # 입사 첫해
        first_year_end = datetime.date(self.hire_date.year, 12, 31)
        days_in_first_year = (first_year_end - self.hire_date).days + 1
        
        # 1년 미만인 경우 - 매월 1일씩 계산 (최대 11일)
        if days_in_first_year < 365:
            months_worked = min(days_in_first_year // 30 + 1, 12)
            # 11월 이상 근무시 12월에는 연차가 발생하지 않음 (최대 11일)
            result[self.hire_date.year] = min(months_worked, 11)
        # 1년 이상인 경우 - 15일 부여
        else:
            result[self.hire_date.year] = 15
            years_worked = 1
        
        # 다음 연도부터 계산
        for year in range(self.hire_date.year + 1, self.calculation_end_date.year + 1):
            # 연초 시점의 근속 연수 계산
            years_at_start_of_year = years_worked + (year - self.hire_date.year - 1)
            
            # 해당 연도가 입사 후 1년 미만인 경우
            if years_at_start_of_year == 0:
                # 해당 연도 1월 1일부터 입사 1주년까지의 월수 계산
                anniversary = datetime.date(self.hire_date.year + 1, self.hire_date.month, self.hire_date.day)
                months_until_anniversary = ((anniversary - datetime.date(year, 1, 1)).days + 1) // 30
                # 남은 달에 대해 1일씩 부여 (최대 11일까지)
                annual_leave = min(months_until_anniversary, 11)
                
                # 입사 1주년부터 해당 연도 말까지의 일수에 대한 15일 비례 계산
                days_after_anniversary = (datetime.date(year, 12, 31) - anniversary).days + 1
                if days_after_anniversary > 0:
                    proportional_leave = 15 * days_after_anniversary / 365
                    annual_leave += math.ceil(proportional_leave)
                
                result[year] = annual_leave
            # 입사 1년 이후
            else:
                # 기본 15일
                annual_leave = 15
                
                # 3년 이상 근속시 2년마다 1일씩 추가 (최대 25일)
                if years_at_start_of_year >= 3:
                    additional_days = min((years_at_start_of_year - 1) // 2, 10)  # 최대 10일 추가
                    annual_leave += additional_days
                
                result[year] = annual_leave
            
            years_worked += 1
            
            # 퇴사한 경우 해당 연도까지만 계산
            if self.termination_date and year == self.termination_date.year:
                # 퇴사일까지의 비례 연차 계산
                days_worked_in_year = (self.termination_date - datetime.date(year, 1, 1)).days + 1
                days_in_year = 366 if calendar.isleap(year) else 365
                result[year] = math.ceil(result[year] * days_worked_in_year / days_in_year)
                break
        
        return result
    
    def get_fiscal_year_leaves(self):
        """
        회계연도 기준 연차휴가 계산
        
        Returns:
            dict: 연도별 연차일수 (키: 연도, 값: 일수)
        """
        result = {}
        
        # 입사 첫해
        first_year_end = datetime.date(self.hire_date.year, 12, 31)
        days_in_first_year = (first_year_end - self.hire_date).days + 1
        
        # 1월 1일 입사인 경우 즉시 15일 부여
        if self.hire_date.month == 1 and self.hire_date.day == 1:
            result[self.hire_date.year] = 15
        # 그 외의 경우 매월 1일씩 계산 (최대 11일)
        else:
            months_in_first_year = 12 - self.hire_date.month + (1 if self.hire_date.day == 1 else 0)
            result[self.hire_date.year] = min(months_in_first_year, 11)
        
        # 다음 회계연도부터 계산
        for year in range(self.hire_date.year + 1, self.calculation_end_date.year + 1):
            # 전년도 재직일수에 따른 비례 연차 계산 또는 15일 기본 부여
            if year == self.hire_date.year + 1:
                # 입사 첫해의 재직일수
                days_worked_prev_year = (datetime.date(year-1, 12, 31) - self.hire_date).days + 1
                
                # 입사일이 1년 미만인 경우 비례 연차
                if days_worked_prev_year < 365:
                    proportional_leave = 15 * days_worked_prev_year / 365
                    annual_leave = math.ceil(proportional_leave)  # 소수점 올림
                # 입사일이 1년 이상인 경우 15일 부여
                else:
                    annual_leave = 15
            else:
                # 1년 이상 근무한 경우
                # 입사 연도부터 현재 연도까지의 근속 연수 계산
                years_worked = (datetime.date(year, 1, 1) - self.hire_date).days // 365
                
                # 기본 15일
                annual_leave = 15
                
                # 3년 이상 근속시 2년마다 1일씩 추가 (최대 25일)
                if years_worked >= 3:
                    additional_days = min((years_worked - 1) // 2, 10)  # 최대 10일 추가
                    annual_leave += additional_days
            
            result[year] = annual_leave
            
            # 퇴사한 경우 해당 연도까지만 계산
            if self.termination_date and year == self.termination_date.year:
                # 퇴사일까지의 비례 연차 계산
                days_worked_in_year = (self.termination_date - datetime.date(year, 1, 1)).days + 1
                days_in_year = 366 if calendar.isleap(year) else 365
                result[year] = math.ceil(result[year] * days_worked_in_year / days_in_year)
                break
        
        return result
    
    def get_employment_year_schedule(self):
        """
        입사연도 기준 연차 발생 일정 계산
        
        Returns:
            list: 연차 발생 일정 리스트 (각 항목은 사전형)
        """
        schedule = []
        
        # 근속 첫 해
        if (datetime.date(self.hire_date.year, 12, 31) - self.hire_date).days < 365:
            # 1년 미만 근무자는 1개월 근무 시 1일씩 발생
            for i in range(min(11, 12 - self.hire_date.month + 1)):
                accrual_date = datetime.date(
                    self.hire_date.year if self.hire_date.month + i <= 12 else self.hire_date.year + 1,
                    (self.hire_date.month + i - 1) % 12 + 1,
                    self.hire_date.day
                )
                
                # 발생일이 퇴사일 이후인 경우 중단
                if self.termination_date and accrual_date > self.termination_date:
                    break
                
                # 발생일이 현재 계산 종료일 이후인 경우 중단
                if accrual_date > self.calculation_end_date:
                    break
                
                expiry_date = accrual_date.replace(year=accrual_date.year + 1)
                
                schedule.append({
                    "발생일": accrual_date,
                    "만료일": min(expiry_date, self.calculation_end_date) if self.termination_date is None else min(expiry_date, self.termination_date),
                    "연차일수": 1,
                    "비고": f"입사 {i+1}개월차"
                })
        else:
            # 입사일에 바로 15일 부여 (1년 이상 근무한 경우)
            expiry_date = self.hire_date.replace(year=self.hire_date.year + 1)
            schedule.append({
                "발생일": self.hire_date,
                "만료일": min(expiry_date, self.calculation_end_date) if self.termination_date is None else min(expiry_date, self.termination_date),
                "연차일수": 15,
                "비고": "1년 이상 근무"
            })
        
        # 입사 1주년부터 매년 입사일마다 연차 발생
        anniversary_date = self.hire_date.replace(year=self.hire_date.year + 1)
        
        for i in range(1, (self.calculation_end_date.year - anniversary_date.year) + 2):
            current_anniversary = anniversary_date.replace(year=anniversary_date.year + i - 1)
            
            # 발생일이 퇴사일 이후인 경우 중단
            if self.termination_date and current_anniversary > self.termination_date:
                break
            
            # 발생일이 현재 계산 종료일 이후인 경우 중단
            if current_anniversary > self.calculation_end_date:
                break
            
            years_worked = i + 1  # 1주년 + i년
            additional_days = min((years_worked - 1) // 2, 10) if years_worked >= 3 else 0
            annual_leave = 15 + additional_days
            
            expiry_date = current_anniversary.replace(year=current_anniversary.year + 1)
            
            schedule.append({
                "발생일": current_anniversary,
                "만료일": min(expiry_date, self.calculation_end_date) if self.termination_date is None else min(expiry_date, self.termination_date),
                "연차일수": annual_leave,
                "비고": f"근속 {years_worked}년차" + (f" (+{additional_days}일)" if additional_days > 0 else "")
            })
        
        return schedule
    
    def get_fiscal_year_schedule(self):
        """
        회계연도 기준 연차 발생 일정 계산
        
        Returns:
            list: 연차 발생 일정 리스트 (각 항목은 사전형)
        """
        schedule = []
        
        # 입사 첫해
        if self.hire_date.month == 1 and self.hire_date.day == 1:
            # 1월 1일 입사는 바로 15일 부여
            expiry_date = datetime.date(self.hire_date.year + 1, 1, 1)
            schedule.append({
                "발생일": self.hire_date,
                "만료일": min(expiry_date, self.calculation_end_date) if self.termination_date is None else min(expiry_date, self.termination_date),
                "연차일수": 15,
                "비고": "1월 1일 입사"
            })
        else:
            # 입사 후 1개월마다 1일씩 발생 (최대 11일)
            months_in_first_year = 12 - self.hire_date.month + (1 if self.hire_date.day == 1 else 0)
            
            for i in range(min(11, months_in_first_year)):
                accrual_date = datetime.date(
                    self.hire_date.year if self.hire_date.month + i <= 12 else self.hire_date.year + 1,
                    (self.hire_date.month + i - 1) % 12 + 1,
                    self.hire_date.day
                )
                
                # 발생일이 퇴사일 이후인 경우 중단
                if self.termination_date and accrual_date > self.termination_date:
                    break
                
                # 발생일이 현재 계산 종료일 이후인 경우 중단
                if accrual_date > self.calculation_end_date:
                    break
                
                expiry_date = datetime.date(self.hire_date.year + 1, 1, 1)
                
                schedule.append({
                    "발생일": accrual_date,
                    "만료일": min(expiry_date, self.calculation_end_date) if self.termination_date is None else min(expiry_date, self.termination_date),
                    "연차일수": 1,
                    "비고": f"입사 {i+1}개월차"
                })
        
        # 입사 다음 해 1월 1일부터 매년 1월 1일마다 연차 발생
        next_fiscal_year = datetime.date(self.hire_date.year + 1, 1, 1)
        
        for i in range(0, (self.calculation_end_date.year - next_fiscal_year.year) + 1):
            current_fiscal_year = next_fiscal_year.replace(year=next_fiscal_year.year + i)
            
            # 발생일이 퇴사일 이후인 경우 중단
            if self.termination_date and current_fiscal_year > self.termination_date:
                break
            
            # 발생일이 현재 계산 종료일 이후인 경우 중단
            if current_fiscal_year > self.calculation_end_date:
                break
            
            # 첫 번째 회계연도의 비례 연차 계산
            if i == 0 and (current_fiscal_year - self.hire_date).days < 365:
                days_worked_prev_year = (datetime.date(current_fiscal_year.year - 1, 12, 31) - self.hire_date).days + 1
                proportional_leave = 15 * days_worked_prev_year / 365
                annual_leave = math.ceil(proportional_leave)  # 소수점 올림
                note = f"비례 연차 (전년도 근무 {days_worked_prev_year}일)"
            else:
                # 입사일부터 현재 회계연도까지의 근속 연수 계산
                years_worked = (current_fiscal_year - self.hire_date).days // 365
                
                # 기본 15일
                annual_leave = 15
                
                # 3년 이상 근속시 2년마다 1일씩 추가 (최대 25일)
                additional_days = 0
                if years_worked >= 3:
                    additional_days = min((years_worked - 1) // 2, 10)  # 최대 10일 추가
                    annual_leave += additional_days
                
                note = f"근속 {years_worked+1}년차" + (f" (+{additional_days}일)" if additional_days > 0 else "")
            
            expiry_date = datetime.date(current_fiscal_year.year + 1, 1, 1)
            
            schedule.append({
                "발생일": current_fiscal_year,
                "만료일": min(expiry_date, self.calculation_end_date) if self.termination_date is None else min(expiry_date, self.termination_date),
                "연차일수": annual_leave,
                "비고": note
            })
        
        return schedule
    
    def generate_annual_leave_table(self, years=5):
        """
        연차휴가 발생 테이블 생성
        
        Args:
            years (int, optional): 계산할 연도 수. 기본값은 5.
            
        Returns:
            pandas.DataFrame: 연차휴가 발생 테이블
        """
        # 입사일 기준 및 회계연도 기준 연차휴가 계산
        employment_year_leaves = self.get_employment_year_leaves()
        fiscal_year_leaves = self.get_fiscal_year_leaves()
        
        # 결과를 담을 데이터 프레임 준비
        data = []
        current_date = self.hire_date
        
        # 각 월별 데이터 생성
        for year in range(self.hire_date.year, self.hire_date.year + years):
            for month in range(1, 13):
                # 입사일 이전 월은 건너뛰기
                if year == self.hire_date.year and month < self.hire_date.month:
                    continue
                
                # 입사일로부터의 근속기간 계산
                current_date = datetime.date(year, month, min(self.hire_date.day, calendar.monthrange(year, month)[1]))
                years_worked = (current_date.year - self.hire_date.year)
                months_worked = (current_date.year - self.hire_date.year) * 12 + (current_date.month - self.hire_date.month)
                
                # 해당 월의 누적 근속일수
                days_worked = (current_date - self.hire_date).days
                
                # 입사일 기준 연차휴가 계산
                employment_leave = 0
                if (current_date - self.hire_date).days < 365:
                    # 1년 미만: 1개월마다 1일씩 (최대 11일)
                    employment_leave = min(months_worked, 11)
                else:
                    # 입사 1주년이 지난 시점 여부 확인
                    anniversary = self.hire_date.replace(year=self.hire_date.year + years_worked)
                    if current_date >= anniversary:
                        base_leave = 15
                        # 3년 이상 근속 시 추가 연차
                        if years_worked >= 3:
                            additional_days = min((years_worked - 1) // 2, 10)
                            base_leave += additional_days
                        employment_leave = base_leave
                    else:
                        # 1년 경과 전 연차: 전년도 발생 연차 사용
                        employment_leave = min(months_worked, 11)
                
                # 회계연도 기준 연차휴가 계산
                fiscal_leave = 0
                if current_date.month == 1 and current_date.day == 1:
                    # 1월 1일에 비례 연차 또는 15일 부여
                    if year == self.hire_date.year + 1:
                        days_worked_prev_year = (datetime.date(year-1, 12, 31) - self.hire_date).days + 1
                        if days_worked_prev_year < 365:
                            fiscal_leave = math.ceil(15 * days_worked_prev_year / 365)
                        else:
                            fiscal_leave = 15
                    else:
                        # 회계연도 기준 연차 계산
                        fiscal_year_worked = (datetime.date(year, 1, 1) - self.hire_date).days // 365
                        base_leave = 15
                        if fiscal_year_worked >= 3:
                            additional_days = min((fiscal_year_worked - 1) // 2, 10)
                            base_leave += additional_days
                        fiscal_leave = base_leave
                else:
                    # 1월 1일이 아닌 경우, 현재 회계연도의 연차
                    if year in fiscal_year_leaves:
                        fiscal_leave = fiscal_year_leaves[year]
                    # 초년도 월별 발생 연차
                    if year == self.hire_date.year and months_worked > 0:
                        fiscal_leave = min(months_worked, 11)
                
                # 데이터 저장
                data.append({
                    "기준일": current_date.strftime("%Y-%m-%d"),
                    "근속기간(년)": years_worked,
                    "근속기간(월)": months_worked,
                    "입사일 기준 연차": employment_leave,
                    "회계연도 기준 연차": fiscal_leave
                })
                
                # 퇴사한 경우 해당 월까지만 계산
                if self.termination_date and current_date >= self.termination_date:
                    break
            
            # 퇴사한 경우 해당 연도까지만 계산
            if self.termination_date and current_date >= self.termination_date:
                break
        
        return pd.DataFrame(data)
    
    def get_annual_leave_comparison(self, years=5):
        """
        입사일 기준과 회계연도 기준 연차휴가 비교
        
        Args:
            years (int, optional): 계산할 연도 수. 기본값은 5.
            
        Returns:
            dict: 비교 정보
        """
        # 연차휴가 발생 테이블
        df = self.generate_annual_leave_table(years)
        
        # 마지막 행 기준 연차휴가 일수
        last_row = df.iloc[-1]
        employment_leave = last_row["입사일 기준 연차"]
        fiscal_leave = last_row["회계연도 기준 연차"]
        
        # 누적 연차휴가 일수
        employment_total = df["입사일 기준 연차"].sum()
        fiscal_total = df["회계연도 기준 연차"].sum()
        
        # 두 방식의 차이
        difference = fiscal_leave - employment_leave
        total_difference = fiscal_total - employment_total
        
        # 각 연도별 연차휴가 일수
        annual_data = {}
        for year in range(self.hire_date.year, self.hire_date.year + years):
            year_df = df[df["기준일"].str.startswith(str(year))]
            if not year_df.empty:
                annual_data[year] = {
                    "입사일 기준": year_df["입사일 기준 연차"].max(),
                    "회계연도 기준": year_df["회계연도 기준 연차"].max()
                }
        
        return {
            "현재 연차일수": {
                "입사일 기준": employment_leave,
                "회계연도 기준": fiscal_leave,
                "차이": difference
            },
            "누적 연차일수": {
                "입사일 기준": employment_total,
                "회계연도 기준": fiscal_total,
                "차이": total_difference
            },
            "연도별 연차일수": annual_data
        }
