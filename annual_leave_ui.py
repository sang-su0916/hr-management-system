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
        total_leaves = 0
        for year, days in employment_year_leaves.items():
            # 누적 연차 계산
            total_leaves += days
            
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
                "누적 연차일수": total_leaves,
                "계산 설명": explanation
            })
        
        # 데이터프레임으로 변환
        df = pd.DataFrame(data)
        st.dataframe(
            df,
            column_config={
                "연도": st.column_config.TextColumn("연도"),
                "연차휴가일수": st.column_config.NumberColumn("연차휴가일수", format="%d일"),
                "근속연수": st.column_config.TextColumn("근속연수"),
                "누적 연차일수": st.column_config.NumberColumn("누적 연차일수", format="%d일"),
                "계산 설명": st.column_config.TextColumn("계산 설명"),
            },
            use_container_width=True,
            hide_index=True
        )
        
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
        
        # 누적 연차 그래프
        fig2 = px.line(
            df,
            x="연도",
            y="누적 연차일수",
            markers=True,
            text="누적 연차일수",
            title="입사일 기준 누적 연차휴가 일수",
            labels={"연도": "연도", "누적 연차일수": "누적 연차일수 (일)"}
        )
        fig2.update_layout(
            xaxis_title="연도",
            yaxis_title="누적 연차일수 (일)"
        )
        st.plotly_chart(fig2, use_container_width=True)
        
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
        total_leaves = 0
        for year, days in fiscal_year_leaves.items():
            # 누적 연차 계산
            total_leaves += days
            
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
                "누적 연차일수": total_leaves,
                "계산 설명": explanation
            })
        
        # 데이터프레임으로 변환
        df = pd.DataFrame(data)
        st.dataframe(
            df,
            column_config={
                "연도": st.column_config.TextColumn("연도"),
                "연차휴가일수": st.column_config.NumberColumn("연차휴가일수", format="%d일"),
                "근속연수": st.column_config.TextColumn("근속연수"),
                "누적 연차일수": st.column_config.NumberColumn("누적 연차일수", format="%d일"),
                "계산 설명": st.column_config.TextColumn("계산 설명"),
            },
            use_container_width=True,
            hide_index=True
        )
        
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
        
        # 누적 연차 그래프
        fig2 = px.line(
            df,
            x="연도",
            y="누적 연차일수",
            markers=True,
            text="누적 연차일수",
            title="회계연도 기준 누적 연차휴가 일수",
            labels={"연도": "연도", "누적 연차일수": "누적 연차일수 (일)"}
        )
        fig2.update_layout(
            xaxis_title="연도",
            yaxis_title="누적 연차일수 (일)"
        )
        st.plotly_chart(fig2, use_container_width=True)
        
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
        st.dataframe(
            df,
            column_config={
                "기준일": st.column_config.TextColumn("기준일"),
                "근속기간(년)": st.column_config.NumberColumn("근속기간(년)", format="%d년"),
                "근속기간(월)": st.column_config.NumberColumn("근속기간(월)", format="%d개월"),
                "입사일 기준 연차": st.column_config.NumberColumn("입사일 기준 연차", format="%d일"),
                "회계연도 기준 연차": st.column_config.NumberColumn("회계연도 기준 연차", format="%d일"),
            },
            use_container_width=True,
            hide_index=True
        )
        
        # 누적 합계 계산
        emp_cumsum = df["입사일 기준 연차"].cumsum()
        fiscal_cumsum = df["회계연도 기준 연차"].cumsum()
        
        # 누적 합계 행 추가
        st.subheader("월별 누적 합계")
        df_cumsum = pd.DataFrame({
            "기준일": df["기준일"],
            "입사일 기준 연차(누적)": emp_cumsum,
            "회계연도 기준 연차(누적)": fiscal_cumsum,
            "차이(회계-입사)": fiscal_cumsum - emp_cumsum
        })
        
        st.dataframe(
            df_cumsum,
            column_config={
                "기준일": st.column_config.TextColumn("기준일"),
                "입사일 기준 연차(누적)": st.column_config.NumberColumn("입사일 기준 연차(누적)", format="%d일"),
                "회계연도 기준 연차(누적)": st.column_config.NumberColumn("회계연도 기준 연차(누적)", format="%d일"),
                "차이(회계-입사)": st.column_config.NumberColumn("차이(회계-입사)", format="%d일"),
            },
            use_container_width=True,
            hide_index=True
        )
        
        # 그래프 표시
        st.subheader("연차휴가 발생 추이")
        
        # 그래프 유형 선택
        chart_type = st.radio(
            "그래프 유형",
            ["일반", "누적"],
            horizontal=True
        )
        
        if chart_type == "일반":
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
        else:
            # 누적 그래프 시각화
            fig = go.Figure()
            
            # 입사일 기준 연차 누적 추가
            fig.add_trace(go.Scatter(
                x=df_cumsum["기준일"],
                y=df_cumsum["입사일 기준 연차(누적)"],
                mode="lines+markers",
                name="입사일 기준(누적)",
                line=dict(color="#1E88E5", width=2),
                marker=dict(size=6),
            ))
            
            # 회계연도 기준 연차 누적 추가
            fig.add_trace(go.Scatter(
                x=df_cumsum["기준일"],
                y=df_cumsum["회계연도 기준 연차(누적)"],
                mode="lines+markers",
                name="회계연도 기준(누적)",
                line=dict(color="#4CAF50", width=2),
                marker=dict(size=6),
            ))
            
            # 차이 추가
            fig.add_trace(go.Bar(
                x=df_cumsum["기준일"],
                y=df_cumsum["차이(회계-입사)"],
                name="차이(회계-입사)",
                marker_color="#FF5722",
            ))
            
            # 그래프 레이아웃 설정
            fig.update_layout(
                title="입사일 기준 vs 회계연도 기준 누적 연차휴가 추이",
                xaxis_title="날짜",
                yaxis_title="누적 연차휴가 일수 (일)",
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
    입사일 기준과 회계연도 기준 비교 표시 (표 형태로 개선)
    """
    st.header("입사일 기준 vs 회계연도 기준 비교")
    
    # 비교 정보 가져오기
    comparison = calculator.get_annual_leave_comparison(years)
    
    # 연도별 비교 데이터 준비
    annual_data = comparison["연도별 연차일수"]
    
    if annual_data:
        # 연차 데이터 준비
        data = []
        emp_cumulative = 0  # 입사일 기준 누적
        fiscal_cumulative = 0  # 회계연도 기준 누적
        
        for year, values in annual_data.items():
            # 누적 계산
            emp_cumulative += values["입사일 기준"]
            fiscal_cumulative += values["회계연도 기준"]
            diff = values["회계연도 기준"] - values["입사일 기준"]
            cumul_diff = fiscal_cumulative - emp_cumulative
            
            data.append({
                "연도": f"{year}년",
                "입사일 기준": values["입사일 기준"],
                "회계연도 기준": values["회계연도 기준"],
                "차이": diff,
                "입사일 기준(누적)": emp_cumulative,
                "회계연도 기준(누적)": fiscal_cumulative,
                "누적 차이": cumul_diff
            })
        
        # 데이터프레임으로 변환
        df = pd.DataFrame(data)
        
        # 비교 결과 표 생성
        st.subheader("연차휴가 비교 테이블")
        
        # 스타일링을 위한 함수
        def highlight_diff(val):
            if isinstance(val, (int, float)):
                if "차이" in val.name and val.value != 0:
                    color = 'green' if val.value > 0 else 'red'
                    return f'color: {color}'
            return ''
        
        # 표 전체 표시 (연도별 + 누적)
        st.dataframe(
            df,
            column_config={
                "연도": st.column_config.TextColumn("연도"),
                "입사일 기준": st.column_config.NumberColumn("입사일 기준", format="%d일"),
                "회계연도 기준": st.column_config.NumberColumn("회계연도 기준", format="%d일"),
                "차이": st.column_config.NumberColumn("차이(회계-입사)", format="%d일", help="양수: 회계연도 기준이 더 많음, 음수: 입사일 기준이 더 많음"),
                "입사일 기준(누적)": st.column_config.NumberColumn("입사일 기준(누적)", format="%d일"),
                "회계연도 기준(누적)": st.column_config.NumberColumn("회계연도 기준(누적)", format="%d일"),
                "누적 차이": st.column_config.NumberColumn("누적 차이", format="%d일", help="양수: 회계연도 기준이 더 많음, 음수: 입사일 기준이 더 많음"),
            },
            use_container_width=True,
            hide_index=True
        )
        
        # 현재 연차와 누적 연차 비교 표 (요약)
        st.subheader("연차휴가 비교 요약")
        
        summary_data = {
            "구분": ["현재 연차일수", "누적 연차일수"],
            "입사일 기준": [
                comparison['현재 연차일수']['입사일 기준'],
                comparison['누적 연차일수']['입사일 기준']
            ],
            "회계연도 기준": [
                comparison['현재 연차일수']['회계연도 기준'],
                comparison['누적 연차일수']['회계연도 기준']
            ],
            "차이(회계-입사)": [
                comparison['현재 연차일수']['차이'],
                comparison['누적 연차일수']['차이']
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        
        # 요약 표 스타일링
        st.dataframe(
            summary_df,
            column_config={
                "구분": st.column_config.TextColumn("구분"),
                "입사일 기준": st.column_config.NumberColumn("입사일 기준", format="%d일"),
                "회계연도 기준": st.column_config.NumberColumn("회계연도 기준", format="%d일"),
                "차이(회계-입사)": st.column_config.NumberColumn("차이(회계-입사)", format="%d일")
            },
            use_container_width=True,
            hide_index=True
        )
        
        # 그래프로 시각화
        st.subheader("연도별 연차휴가 비교")
        
        # 시각화 유형 선택
        viz_type = st.radio(
            "시각화 유형",
            ["연도별 연차일수", "누적 연차일수"],
            horizontal=True
        )
        
        if viz_type == "연도별 연차일수":
            # 연도별 연차일수 막대 그래프
            fig = go.Figure()
            
            # 입사일 기준 연차 막대 추가
            fig.add_trace(go.Bar(
                x=df["연도"],
                y=df["입사일 기준"],
                name="입사일 기준",
                marker_color="#1E88E5",
                text=df["입사일 기준"],
                textposition="auto"
            ))
            
            # 회계연도 기준 연차 막대 추가
            fig.add_trace(go.Bar(
                x=df["연도"],
                y=df["회계연도 기준"],
                name="회계연도 기준",
                marker_color="#4CAF50",
                text=df["회계연도 기준"],
                textposition="auto"
            ))
            
            # 차이 표시 (선 그래프)
            fig.add_trace(go.Scatter(
                x=df["연도"],
                y=df["차이"],
                name="차이(회계-입사)",
                mode="lines+markers+text",
                marker=dict(size=8, color="#FF5722"),
                line=dict(color="#FF5722", width=2, dash="dot"),
                text=df["차이"],
                textposition="top center"
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
        else:
            # 누적 연차일수 그래프
            fig2 = go.Figure()
            
            # 입사일 기준 누적 연차 추가
            fig2.add_trace(go.Scatter(
                x=df["연도"],
                y=df["입사일 기준(누적)"],
                mode="lines+markers+text",
                name="입사일 기준(누적)",
                line=dict(color="#1E88E5", width=2),
                marker=dict(size=8),
                text=df["입사일 기준(누적)"],
                textposition="top center"
            ))
            
            # 회계연도 기준 누적 연차 추가
            fig2.add_trace(go.Scatter(
                x=df["연도"],
                y=df["회계연도 기준(누적)"],
                mode="lines+markers+text",
                name="회계연도 기준(누적)",
                line=dict(color="#4CAF50", width=2),
                marker=dict(size=8),
                text=df["회계연도 기준(누적)"],
                textposition="top center"
            ))
            
            # 누적 차이 추가 (막대 그래프)
            fig2.add_trace(go.Bar(
                x=df["연도"],
                y=df["누적 차이"],
                name="누적 차이(회계-입사)",
                marker_color="#FF5722",
                text=df["누적 차이"],
                textposition="auto"
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
        
        # 연차휴가 계산기 해석
        with st.expander("연차휴가 비교 결과 해석", expanded=False):
            st.markdown("""
            ### 연차휴가 비교 결과 해석
            
            **현재 연차일수**:
            - 입사일 기준과 회계연도 기준의 현재 보유 연차일수를 비교합니다.
            - 차이가 양수면 회계연도 기준이 더 많고, 음수면 입사일 기준이 더 많습니다.
            
            **누적 연차일수**:
            - 입사 이후부터 전체 기간 동안 발생한 총 연차일수를 비교합니다.
            - 이 값을 통해 장기적으로 어떤 방식이 더 유리한지 파악할 수 있습니다.
            
            **연도별 비교**:
            - 각 연도마다 두 방식으로 계산된 연차일수와 그 차이를 보여줍니다.
            - 특정 시점에 유리한 방식이 어떻게 변화하는지 확인할 수 있습니다.
            """)
    
    else:
        st.warning("연차휴가 비교 데이터가 없습니다.")
    
    # 두 방식의 특징 설명
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
