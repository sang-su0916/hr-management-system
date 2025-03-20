import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import sys
import os

# 연차휴가 계산기 클래스 임포트 (수정됨)
from annual_leave_calculator import AnnualLeaveCalculator

def render_annual_leave_calculator():
    """
    연차휴가 계산기 UI 렌더링 함수
    """
    st.title("🗓️ 연차휴가 계산기")
    
    # 탭 생성
    tabs = st.tabs(["입사일 기준 계산", "회계연도 기준 계산", "연차휴가 발생 테이블"])
    
    # 연차휴가 계산기 인스턴스 생성
    calculator = AnnualLeaveCalculator()
    
    # 입사일 기준 계산 탭
    with tabs[0]:
        st.header("입사일 기준 연차휴가 계산")
        
        col1, col2 = st.columns(2)
        
        with col1:
            entry_date = st.date_input(
                "입사일",
                value=datetime.date.today() - datetime.timedelta(days=365),
                min_value=datetime.date(1990, 1, 1),
                max_value=datetime.date.today(),
                format="YYYY-MM-DD"
            )
        
        with col2:
            target_date = st.date_input(
                "기준일 (선택사항)",
                value=datetime.date.today(),
                min_value=entry_date,
                format="YYYY-MM-DD"
            )
        
        if st.button("계산하기", key="entry_date_calc"):
            result = calculator.calculate_by_entry_date(entry_date, target_date)
            
            # 결과 표시
            st.subheader("계산 결과")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("근속 기간 (년)", f"{result['years_worked']}년")
            
            with col2:
                st.metric("근속 기간 (월)", f"{result['months_worked']}개월")
            
            with col3:
                st.metric("연차휴가 일수", f"{result['annual_leave_days']}일")
            
            st.info(f"다음 연차 발생일: {result['next_annual_leave_date']}")
            
            # 연차휴가 발생 그래프
            st.subheader("연차휴가 발생 추이")
            df = calculator.generate_annual_leave_table(entry_date, years=5)
            
            fig = px.line(
                df,
                x="기준일",
                y="연차휴가일수",
                markers=True,
                title="연차휴가 발생 추이 (5년)",
                labels={"기준일": "날짜", "연차휴가일수": "연차휴가 일수"}
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # 회계연도 기준 계산 탭
    with tabs[1]:
        st.header("회계연도 기준 연차휴가 계산")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            entry_date = st.date_input(
                "입사일",
                value=datetime.date.today() - datetime.timedelta(days=365),
                min_value=datetime.date(1990, 1, 1),
                max_value=datetime.date.today(),
                format="YYYY-MM-DD",
                key="fiscal_entry_date"
            )
        
        with col2:
            fiscal_year_start = st.text_input("회계연도 시작일 (MM-DD)", "01-01")
        
        with col3:
            fiscal_year_end = st.text_input("회계연도 종료일 (MM-DD)", "12-31")
        
        if st.button("계산하기", key="fiscal_year_calc"):
            result = calculator.calculate_by_fiscal_year(entry_date, fiscal_year_start, fiscal_year_end)
            
            # 결과 표시
            st.subheader("회계연도별 연차휴가")
            
            # 회계연도별 연차휴가 테이블
            fiscal_years_data = result["fiscal_years"]
            
            if fiscal_years_data:
                df = pd.DataFrame(fiscal_years_data)
                df = df.rename(columns={
                    "fiscal_year": "회계연도",
                    "fiscal_year_start": "시작일",
                    "fiscal_year_end": "종료일",
                    "annual_leave_days": "연차휴가일수"
                })
                
                st.dataframe(df, use_container_width=True)
                
                # 회계연도별 연차휴가 그래프
                fig = px.bar(
                    df,
                    x="회계연도",
                    y="연차휴가일수",
                    title="회계연도별 연차휴가 일수",
                    labels={"회계연도": "회계연도", "연차휴가일수": "연차휴가 일수"}
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("표시할 회계연도 데이터가 없습니다.")
    
    # 연차휴가 발생 테이블 탭
    with tabs[2]:
        st.header("연차휴가 발생 테이블")
        
        col1, col2 = st.columns(2)
        
        with col1:
            entry_date = st.date_input(
                "입사일",
                value=datetime.date.today() - datetime.timedelta(days=365),
                min_value=datetime.date(1990, 1, 1),
                max_value=datetime.date.today(),
                format="YYYY-MM-DD",
                key="table_entry_date"
            )
        
        with col2:
            years = st.slider("계산 기간 (년)", 1, 10, 5)
        
        if st.button("테이블 생성", key="table_gen"):
            df = calculator.generate_annual_leave_table(entry_date, years=years)
            
            # 테이블 표시
            st.dataframe(df, use_container_width=True)
            
            # 그래프 표시
            st.subheader("연차휴가 발생 추이")
            
            fig = px.line(
                df,
                x="기준일",
                y="연차휴가일수",
                markers=True,
                title=f"연차휴가 발생 추이 ({years}년)",
                labels={"기준일": "날짜", "연차휴가일수": "연차휴가 일수"}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 엑셀 다운로드 버튼
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="CSV 다운로드",
                data=csv,
                file_name=f"연차휴가_발생_테이블_{entry_date.strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

if __name__ == "__main__":
    render_annual_leave_calculator()
