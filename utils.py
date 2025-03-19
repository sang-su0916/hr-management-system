"""
utils.py - 유틸리티 함수 모듈

HR 관리 시스템에서 공통으로 사용되는 유틸리티 함수들을 제공합니다.
"""

import os
import base64
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

def create_directory_if_not_exists(directory_path):
    """
    디렉토리가 존재하지 않는 경우 생성합니다.
    
    Args:
        directory_path (str): 생성할 디렉토리 경로
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def get_download_link(file_path, link_text, file_name=None):
    """
    파일 다운로드 링크를 생성합니다.
    
    Args:
        file_path (str): 다운로드할 파일 경로
        link_text (str): 링크 텍스트
        file_name (str, optional): 다운로드 시 파일 이름. 기본값은 None.
        
    Returns:
        str: HTML 다운로드 링크
    """
    if file_name is None:
        file_name = os.path.basename(file_path)
    
    with open(file_path, "rb") as file:
        file_data = file.read()
    
    b64 = base64.b64encode(file_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}">{link_text}</a>'
    
    return href

def format_currency(amount, currency="원"):
    """
    금액을 통화 형식으로 포맷팅합니다.
    
    Args:
        amount (float): 포맷팅할 금액
        currency (str, optional): 통화 단위. 기본값은 "원".
        
    Returns:
        str: 포맷팅된 금액 문자열
    """
    return f"{amount:,.0f}{currency}"

def calculate_age(birth_date):
    """
    생년월일로부터 나이를 계산합니다.
    
    Args:
        birth_date (datetime.date): 생년월일
        
    Returns:
        int: 나이
    """
    today = datetime.now().date()
    age = today.year - birth_date.year
    
    # 생일이 지나지 않은 경우 1을 빼줌
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    
    return age

def get_month_start_end(year, month):
    """
    특정 연도와 월의 시작일과 종료일을 반환합니다.
    
    Args:
        year (int): 연도
        month (int): 월
        
    Returns:
        tuple: (시작일, 종료일) 튜플
    """
    start_date = datetime(year, month, 1).date()
    
    # 다음 달의 1일에서 하루를 빼서 이번 달의 마지막 날을 구함
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    return start_date, end_date

def apply_custom_css():
    """
    커스텀 CSS 스타일을 적용합니다.
    """
    css = """
    <style>
        .main-header {
            font-size: 2.5rem;
            color: #1E88E5;
            text-align: center;
            margin-bottom: 1rem;
            font-weight: bold;
        }
        
        .sub-header {
            font-size: 1.5rem;
            color: #424242;
            margin-bottom: 1rem;
        }
        
        .info-box {
            background-color: #E3F2FD;
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        
        div[data-testid="stForm"] {
            background-color: #F5F5F5;
            padding: 1.5rem;
            border-radius: 0.5rem;
        }
        
        div[data-testid="stFormSubmitButton"] > button {
            background-color: #1E88E5;
            color: white;
            font-weight: bold;
            border-radius: 0.5rem;
            padding: 0.5rem 2rem;
        }
        
        div[data-testid="metric-container"] {
            background-color: #F5F5F5;
            border-radius: 0.5rem;
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def create_data_frame_with_dummy_data(columns, num_rows=5):
    """
    더미 데이터가 포함된 데이터프레임을 생성합니다.
    
    Args:
        columns (list): 데이터프레임 열 이름 목록
        num_rows (int, optional): 생성할 행 수. 기본값은 5.
        
    Returns:
        pandas.DataFrame: 더미 데이터가 포함된 데이터프레임
    """
    data = {}
    
    for col in columns:
        if "date" in col.lower() or "일" in col:
            # 날짜 형식 데이터
            start_date = datetime.now().date()
            data[col] = [(start_date - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(num_rows)]
        elif "amount" in col.lower() or "금액" in col or "급여" in col or "수당" in col:
            # 금액 형식 데이터
            data[col] = [round(1000000 + i * 100000) for i in range(num_rows)]
        elif "name" in col.lower() or "이름" in col:
            # 이름 형식 데이터
            names = ["홍길동", "김철수", "이영희", "박민수", "정지원"]
            data[col] = names[:num_rows]
        elif "id" in col.lower():
            # ID 형식 데이터
            data[col] = [f"ID{i+1:04d}" for i in range(num_rows)]
        else:
            # 기타 텍스트 데이터
            data[col] = [f"{col} {i+1}" for i in range(num_rows)]
    
    return pd.DataFrame(data)
