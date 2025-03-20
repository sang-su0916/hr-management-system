import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import datetime
import math
from annual_leave_calculator import AnnualLeaveCalculator

def render_annual_leave_calculator():
    """
    연차휴가 계산기 UI 렌더링 함수
    """
    st.title("🗓️ 연차휴가 계산기")
    
    # 계산기 설명
    with st.expander("연차휴가 계산 방식 안내", expanded=False):
        st.markdown("""
        ## 연차휴가 계산: 입사연도 기준 vs. 회계연도 기준
        
        ### 입사연도 기준 연차 계산
        입사일을 기준으로 연차를 계산할 경우, 근로자의 입사일을 기점으로 연차가 발생합니다.
        
        **1년 미만 근로자:**
        * 매월 만근 시 1일의 유급휴가가 발생하며, 최대 11일까지 부여됩니다.
        * 발생된 휴가는 입사일로부터 1년 내에 사용 가능합니다.
        
        **1년 이상 근로자:**
        * 입사일 기준으로 매년 15일의 유급휴가가 부여됩니다.
        * 3년 이상 근속 시, 최초 1년을 초과하는 매 2년마다 1일씩 추가 연차가 가산됩니다 (최대 25일).
        
        ### 회계연도 기준 연차 계산
        회계연도(1월 1일)를 기준으로 연차를 계산할 경우, 모든 근로자의 연차가 동일한 시점에 발생합니다.
        
        **1년 미만 근로자:**
        * 매월 만근 시 1일의 유급휴가가 발생하며, 최대 11일까지 부여됩니다.
        * 다음 회계연도(1월 1일)에 비례 연차가 추가로 부여됩니다. 비례 연차는 전년도 재직일수에 비례하여 계산됩니다.
          * 비례 연차 = 15 × (전년도 재직일수 ÷ 365), 소수점 올림
        
        **1년 이상 근로자:**
        * 매년 1월 1일에 15일의 유급휴가가 부여됩니다.
        * 3년 이상 근속 시, 최초 1년을 초과하는 매 2년마다 1일씩 추가 연차가 가산됩니다 (최대 25일).
        """)
    
    # 입력 폼
    st.subheader("직원 정보 입력")
    
    col1, col2 = st.columns(2)
    
    with col1:
        hire_date = st.date_input(
            "입사일",
            value=datetime.date.today() - datetime.timedelta(days=365),
            min_value=datetime.date(1990, 1, 1),
            max_value=datetime.date.today(),
            key="hire_date"
        )
    
    with col2:
        use_termination_date = st.checkbox("퇴사일 설정", value=False, key="use_termination_date")
        
        termination_date = None
        if use_termination_date:
            termination_date = st.date_input(
                "퇴사일",
                value=datetime.date.today() + datetime.timedelta(days=30),
                min_value=hire_date,
                max_value=datetime.date.today() + datetime.timedelta(days=365*10),
                key="termination_date"
            )
    
    # 계산 기간 설정
    years = st.slider(
        "계산 기간 (년)",
        min_value=1,
        max_value=10,
        value=5,
        help="연차휴가를 계산할 기간을 선택하세요."
    )
    
    # 계산 버튼
    if st.button("연차 계산하기", key="calculate_leave"):
        # 연차 계산
        calculator = AnnualLeaveCalculator(hire_date, termination_date)
        
        # 탭 생성
        tabs = st.tabs(["입사일 기준 계산", "회계연도 기준 계산", "연차휴가 발생 테이블", "두 방식 비교"])
        
        # 입사일 기준 계산 탭
        with tabs[0]:
            display_employment_year_calculation(calculator, years)
        
        # 회계연도 기준 계산 탭
        with tabs[1]:
            display_fiscal_year_calculation(calculator, years)
        
        # 연차휴가 발생 테이블 탭
        with tabs[2]:
            display_annual_leave_table(calculator, years)
        
        # 두 방식 비교 탭
        with tabs[3]:
            display_comparison(calculator, years)

def display_employment_year_calculation(calculator, years):
    """
    입사일 기준 계산 결과 표시
    """
    st.header("입사일 기준 연차휴가 계산")
    
    # 근속 기간 정보
    if calculator.termination_date:
        employment_days = (calculator.termination_date - calculator.hire_date).days
        employment_years = employment_days / 365
        st.write(f"총 근속기간: {employment_days}일 (약 {employment_years:.1f}년)")
    else:
        today = datetime.date.today()
        employment_days = (today - calculator.hire_date).days
        employment_years = employment_days / 365
        st.write(f"현재까지 근속기간: {employment_days}일 (약 {employment_years:.1f}년)")
    
    # 연차휴가 계산 결과
    employment_year_leaves = calculator.get_employment_year_leaves()
    
    # 결과 시각화
    if employment_year_leaves:
        # 데이터 준비
        years = list(employment_year_leaves.keys())
        leaves = list(employment_year_leaves.values())
        
        # 테이블 형태로 표시
        st.subheader("연차휴가 일수")
        
        data = []
        for year, days in employment_year_leaves.items():
            # 해당 연도 종료 시점의 근속 연수 계산
            year_end = datetime.date(year, 12, 31)
            years_worked = (year_end.year - calculator.hire_date.year)
            if year_end.month < calculator.hire_date.month or (year_end.month == calculator.hire_date.month and year_end.day < calculator.hire_date.day):
                years_worked -= 1
            
            # 설명 추가
            explanation = ""
            if (datetime.date(year, 12, 31) - calculator.hire_date).days < 365:
                explanation = "1년 미만 근무: 매월 1일씩 (최대 11일)"
            else:
                if years_worked >= 3:
                    additional_days = min((years_worked - 1) // 2, 10)
                    explanation = f"기본 15일 + 추가 {additional_days}일 (근속 {years_worked}년차)"
                else:
                    explanation = "기본 15일 (근속 1~2년차)"
            
            data.append({
                "연도": str(year) + "년",
                "연차휴가일수": days,
                "근속연수": f"{years_worked}년차",
                "계산 설명": explanation
            })
        
        # 데이터프레임으로 변환
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # 그래프로 시각화
        fig = px.bar(
            df,
            x="연도",
            y="연차휴가일수",
            text="연차휴가일수",
            color="연차휴가일수",
            color_continuous_scale=px.colors.sequential.Blues,
            title="입사일 기준 연도별 연차휴가 일수",
            labels={"연도": "연도", "연차휴가일수": "연차휴가 일수 (일)"}
        )
        fig.update_layout(
            xaxis_title="연도",
            yaxis_title="연차휴가 일수 (일)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 연차휴가 발생 일정 표시
        st.subheader("연차휴가 발생 일정")
        schedule = calculator.get_employment_year_schedule()
        
        if schedule:
            schedule_df = pd.DataFrame(schedule)
            # 날짜 형식 변환
            schedule_df["발생일"] = pd.to_datetime(schedule_df["발생일"]).dt.strftime("%Y-%m-%d")
            schedule_df["만료일"] = pd.to_datetime(schedule_df["만료일"]).dt.strftime("%Y-%m-%d")
            
            st.dataframe(schedule_df, use_container_width=True, hide_index=True)
    
    else:
        st.warning("연차휴가 계산 결과가 없습니다.")

def display_fiscal_year_calculation(calculator, years):
    """
    회계연도 기준 계산 결과 표시
    """
    st.header("회계연도 기준 연차휴가 계산")
    
    # 근속 기간 정보
    if calculator.termination_date:
        employment_days = (calculator.termination_date - calculator.hire_date).days
        employment_years = employment_days / 365
        st.write(f"총 근속기간: {employment_days}일 (약 {employment_years:.1f}년)")
    else:
        today = datetime.date.today()
        employment_days = (today - calculator.hire_date).days
        employment_years = employment_days / 365
        st.write(f"현재까지 근속기간: {employment_days}일 (약 {employment_years:.1f}년)")
    
    # 연차휴가 계산 결과
    fiscal_year_leaves = calculator.get_fiscal_year_leaves()
    
    # 결과 시각화
    if fiscal_year_leaves:
        # 데이터 준비
        years = list(fiscal_year_leaves.keys())
        leaves = list(fiscal_year_leaves.values())
        
        # 테이블 형태로 표시
        st.subheader("연차휴가 일수")
        
        data = []
        for year, days in fiscal_year_leaves.items():
            # 해당 연도 시작 시점의 근속 연수 계산
            year_start = datetime.date(year, 1, 1)
            years_worked = (year_start.year - calculator.hire_date.year)
            if year_start.month < calculator.hire_date.month or (year_start.month == calculator.hire_date.month and year_start.day < calculator.hire_date.day):
                years_worked -= 1
            
            # 설명 추가
            explanation = ""
            if year == calculator.hire_date.year:
                months_remaining = 12 - calculator.hire_date.month + 1
                explanation = f"입사 첫해: 매월 1일씩 (최대 {min(months_remaining, 11)}일)"
            elif year == calculator.hire_date.year + 1:
                days_worked_prev_year = (datetime.date(year-1, 12, 31) - calculator.hire_date).days + 1
                if days_worked_prev_year < 365:
                    explanation = f"비례 연차: 15 × ({days_worked_prev_year}일 ÷ 365일) = {math.ceil(15 * days_worked_prev_year / 365)}일"
                else:
                    explanation = "1년 이상 근무: 15일"
            else:
                if years_worked >= 3:
                    additional_days = min((years_worked - 1) // 2, 10)
                    explanation = f"기본 15일 + 추가 {additional_days}일 (근속 {years_worked}년차)"
                else:
                    explanation = "기본 15일 (근속 1~2년차)"
            
            data.append({
                "연도": str(year) + "년",
                "연차휴가일수": days,
                "근속연수": f"{years_worked}년차",
                "계산 설명": explanation
            })
        
        # 데이터프레임으로 변환
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # 그래프로 시각화
        fig = px.bar(
            df,
            x="연도",
            y="연차휴가일수",
            text="연차휴가일수",
            color="연차휴가일수",
            color_continuous_scale=px.colors.sequential.Greens,
            title="회계연도 기준 연도별 연차휴가 일수",
            labels={"연도": "연도", "연차휴가일수": "연차휴가 일수 (일)"}
        )
        fig.update_layout(
            xaxis_title="연도",
            yaxis_title="연차휴가 일수 (일)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 연차휴가 발생 일정 표시
        st.subheader("연차휴가 발생 일정")
        schedule = calculator.get_fiscal_year_schedule()
        
        if schedule:
            schedule_df = pd.DataFrame(schedule)
            # 날짜 형식 변환
            schedule_df["발생일"] = pd.to_datetime(schedule_df["발생일"]).dt.strftime("%Y-%m-%d")
            schedule_df["만료일"] = pd.to_datetime(schedule_df["만료일"]).dt.strftime("%Y-%m-%d")
            
            st.dataframe(schedule_df, use_container_width=True, hide_index=True)
    
    else:
        st.warning("연차휴가 계산 결과가 없습니다.")

def display_annual_leave_table(calculator, years):
    """
    연차휴가 발생 테이블 표시
    """
    st.header("연차휴가 발생 테이블")
    
    # 연차휴가 발생 테이블 생성
    df = calculator.generate_annual_leave_table(years)
    
    if not df.empty:
        # 테이블 표시
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # 그래프 표시
        st.subheader("연차휴가 발생 추이")
        
        # 라인 그래프로 시각화
        fig = go.Figure()
        
        # 입사일 기준 연차 추가
        fig.add_trace(go.Scatter(
            x=df["기준일"],
            y=df["입사일 기준 연차"],
            mode="lines+markers",
            name="입사일 기준",
            line=dict(color="#1E88E5", width=2),
            marker=dict(size=6),
        ))
        
        # 회계연도 기준 연차 추가
        fig.add_trace(go.Scatter(
            x=df["기준일"],
            y=df["회계연도 기준 연차"],
            mode="lines+markers",
            name="회계연도 기준",
            line=dict(color="#4CAF50", width=2),
            marker=dict(size=6),
        ))
        
        # 그래프 레이아웃 설정
        fig.update_layout(
            title="입사일 기준 vs 회계연도 기준 연차휴가 발생 추이",
            xaxis_title="날짜",
            yaxis_title="연차휴가 일수 (일)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 다운로드 버튼
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="CSV 파일 다운로드",
            data=csv,
            file_name=f"연차휴가_발생_테이블_{calculator.hire_date.strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    else:
        st.warning("연차휴가 발생 테이블을 생성할 수 없습니다.")

def display_comparison(calculator, years):
    """
    입사일 기준과 회계연도 기준 비교 표시
    """
    st.header("입사일 기준 vs 회계연도 기준 비교")
    
    # 비교 정보 가져오기
    comparison = calculator.get_annual_leave_comparison(years)
    
    # 현재 연차일수 비교
    st.subheader("현재 연차일수 비교")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "입사일 기준",
            f"{comparison['현재 연차일수']['입사일 기준']}일"
        )
    
    with col2:
        st.metric(
            "회계연도 기준",
            f"{comparison['현재 연차일수']['회계연도 기준']}일"
        )
    
    with col3:
        delta = comparison['현재 연차일수']['차이']
        st.metric(
            "차이 (회계연도 - 입사일)",
            f"{abs(delta)}일",
            delta=f"{delta}일" if delta != 0 else "0일",
            delta_color="normal"
        )
    
    # 누적 연차일수 비교
    st.subheader("누적 연차일수 비교")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "입사일 기준 (누적)",
            f"{comparison['누적 연차일수']['입사일 기준']}일"
        )
    
    with col2:
        st.metric(
            "회계연도 기준 (누적)",
            f"{comparison['누적 연차일수']['회계연도 기준']}일"
        )
    
    with col3:
        total_delta = comparison['누적 연차일수']['차이']
        st.metric(
            "누적 차이 (회계연도 - 입사일)",
            f"{abs(total_delta)}일",
            delta=f"{total_delta}일" if total_delta != 0 else "0일",
            delta_color="normal"
        )
    
    # 연도별 비교
    st.subheader("연도별 연차일수 비교")
    
    annual_data = comparison["연도별 연차일수"]
    
    if annual_data:
        # 데이터 준비
        data = []
        for year, values in annual_data.items():
            data.append({
                "연도": str(year),
                "입사일 기준": values["입사일 기준"],
                "회계연도 기준": values["회계연도 기준"],
                "차이": values["회계연도 기준"] - values["입사일 기준"]
            })
        
        # 데이터프레임으로 변환
        df = pd.DataFrame(data)
        
        # 테이블 표시
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # 그래프로 시각화
        fig = go.Figure()
        
        # 입사일 기준 연차 막대 추가
        fig.add_trace(go.Bar(
            x=df["연도"],
            y=df["입사일 기준"],
            name="입사일 기준",
            marker_color="#1E88E5"
        ))
        
        # 회계연도 기준 연차 막대 추가
        fig.add_trace(go.Bar(
            x=df["연도"],
            y=df["회계연도 기준"],
            name="회계연도 기준",
            marker_color="#4CAF50"
        ))
        
        # 그래프 레이아웃 설정
        fig.update_layout(
            title="연도별 연차휴가 일수 비교",
            xaxis_title="연도",
            yaxis_title="연차휴가 일수 (일)",
            barmode="group",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 누적 차트
        st.subheader("누적 연차일수 비교")
        
        # 누적 데이터 계산
        df["입사일 기준 (누적)"] = df["입사일 기준"].cumsum()
        df["회계연도 기준 (누적)"] = df["회계연도 기준"].cumsum()
        df["누적 차이"] = df["회계연도 기준 (누적)"] - df["입사일 기준 (누적)"]
        
        # 누적 차트 생성
        fig2 = go.Figure()
        
        # 입사일 기준 누적 연차 추가
        fig2.add_trace(go.Scatter(
            x=df["연도"],
            y=df["입사일 기준 (누적)"],
            mode="lines+markers",
            name="입사일 기준 (누적)",
            line=dict(color="#1E88E5", width=2),
            marker=dict(size=8)
        ))
        
        # 회계연도 기준 누적 연차 추가
        fig2.add_trace(go.Scatter(
            x=df["연도"],
            y=df["회계연도 기준 (누적)"],
            mode="lines+markers",
            name="회계연도 기준 (누적)",
            line=dict(color="#4CAF50", width=2),
            marker=dict(size=8)
        ))
        
        # 그래프 레이아웃 설정
        fig2.update_layout(
            title="누적 연차휴가 일수 비교",
            xaxis_title="연도",
            yaxis_title="누적 연차휴가 일수 (일)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig2, use_container_width=True)
    
    else:
        st.warning("연도별 비교 데이터가 없습니다.")
    
    # 비교표 및 결론
    st.subheader("두 방식 비교표")
    
    comparison_data = {
        "기준": ["1년 미만 근로자", "1년 이상 근로자", "3년 이상 근로자"],
        "입사연도 기준": [
            "매월 만근 시 1일, 최대 11일", 
            "매년 15일", 
            "매 2년마다 1일 추가 (최대 25일)"
        ],
        "회계연도 기준": [
            "매월 만근 시 1일, 최대 11일 + 비례 연차", 
            "매년 15일", 
            "매 2년마다 1일 추가 (최대 25일)"
        ]
    }
    
    comparison_df = pd.DataFrame(comparison_data)
    st.table(comparison_df)
    
    # 결론
    st.info("""
    ### 결론
    
    * **입사연도 기준**은 개별 근로자의 입사일을 기준으로 연차가 발생하므로 관리가 복잡할 수 있으나, 공정한 연차 부여가 가능합니다.
    * **회계연도 기준**은 모든 근로자의 연차를 동일한 시점에 발생시키므로 관리가 편리하나, 중도 입사자의 경우 비례 연차 계산이 필요합니다.
    
    각 회사의 규정에 따라 적절한 기준을 선택하여 연차를 관리하는 것이 중요합니다.
    """)
