import streamlit as st
import os
import sys
from streamlit_option_menu import option_menu
from PIL import Image
import base64

# 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 각 모듈 임포트
from annual_leave.annual_leave_ui import render_annual_leave_calculator
from employment_contract.employment_contract import render_employment_contract_form
from payroll_ledger.payroll_ledger import render_payroll_ledger_ui
from pay_statement.pay_statement import render_pay_statement_ui

# 페이지 설정
st.set_page_config(
    page_title="HR 관리 시스템",
    page_icon="👨‍💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 적용
def load_css():
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
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 4rem;
            white-space: pre-wrap;
            background-color: #F5F5F5;
            border-radius: 0.5rem 0.5rem 0 0;
            padding: 1rem;
            font-weight: bold;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #1E88E5 !important;
            color: white !important;
        }
        
        div[data-testid="stSidebarNav"] {
            background-image: linear-gradient(#1E88E5, #64B5F6);
            padding-top: 2rem;
            border-radius: 0.5rem;
        }
        
        div[data-testid="stSidebarNav"] li {
            margin-bottom: 0.5rem;
        }
        
        div[data-testid="stSidebarNav"] li > div {
            border-radius: 0.5rem;
            padding: 0.5rem;
        }
        
        div[data-testid="stSidebarNav"] li > div:hover {
            background-color: rgba(255, 255, 255, 0.2);
        }
        
        div[data-testid="stSidebarNav"] li > div[aria-selected="true"] {
            background-color: rgba(255, 255, 255, 0.3);
        }
        
        div[data-testid="stSidebarNav"] span {
            color: white;
            font-weight: bold;
        }
        
        div[data-testid="stSidebarNav"] span:hover {
            color: white;
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
        
        div[data-testid="stFormSubmitButton"] > button:hover {
            background-color: #1976D2;
        }
        
        div[data-testid="metric-container"] {
            background-color: #F5F5F5;
            border-radius: 0.5rem;
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.24);
        }
        
        div[data-testid="stDataFrame"] {
            border-radius: 0.5rem;
            overflow: hidden;
        }
        
        div[data-testid="stDataFrame"] table {
            border-collapse: collapse;
        }
        
        div[data-testid="stDataFrame"] th {
            background-color: #1E88E5;
            color: white;
            font-weight: bold;
            padding: 0.5rem;
        }
        
        div[data-testid="stDataFrame"] td {
            padding: 0.5rem;
        }
        
        div[data-testid="stDataFrame"] tr:nth-child(even) {
            background-color: #F5F5F5;
        }
        
        div[data-testid="stDataFrame"] tr:hover {
            background-color: #E3F2FD;
        }
        
        button[kind="primary"] {
            background-color: #1E88E5;
            color: white;
            font-weight: bold;
            border-radius: 0.5rem;
            padding: 0.5rem 2rem;
        }
        
        button[kind="primary"]:hover {
            background-color: #1976D2;
        }
        
        button[kind="secondary"] {
            background-color: #F5F5F5;
            color: #424242;
            font-weight: bold;
            border-radius: 0.5rem;
            padding: 0.5rem 2rem;
            border: 1px solid #BDBDBD;
        }
        
        button[kind="secondary"]:hover {
            background-color: #EEEEEE;
        }
        
        .footer {
            text-align: center;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #EEEEEE;
            color: #9E9E9E;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# 배경 이미지 설정
def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    
    bg_image = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{encoded_string}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    
    st.markdown(bg_image, unsafe_allow_html=True)

# 배경 이미지 파일 생성
def create_background_image():
    # 배경 이미지 디렉토리 생성
    image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static/images")
    os.makedirs(image_dir, exist_ok=True)
    
    # 배경 이미지 파일 경로
    bg_image_path = os.path.join(image_dir, "background.png")
    
    # 배경 이미지가 없는 경우 생성
    if not os.path.exists(bg_image_path):
        # 간단한 그라데이션 배경 이미지 생성
        from PIL import Image, ImageDraw
        
        width, height = 1920, 1080
        image = Image.new("RGBA", (width, height), color=(255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        # 그라데이션 효과 (상단: 밝은 파란색, 하단: 흰색)
        for y in range(height):
            # 상단에서 하단으로 갈수록 투명도 증가
            alpha = int(255 * (1 - y / height * 0.8))
            draw.line([(0, y), (width, y)], fill=(30, 136, 229, alpha))
        
        # 이미지 저장
        image.save(bg_image_path)
    
    return bg_image_path

# 메인 함수
def main():
    # CSS 스타일 적용
    load_css()
    
    # 배경 이미지 설정
    bg_image_path = create_background_image()
    add_bg_from_local(bg_image_path)
    
    # 세션 상태 초기화
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "홈"
    
    # 사이드바 메뉴
    with st.sidebar:
        st.title("HR 관리 시스템")
        
        selected = option_menu(
            menu_title=None,
            options=["홈", "연차휴가 계산기", "근로계약서", "임금대장", "임금명세서"],
            icons=["house", "calendar-check", "file-earmark-text", "cash-coin", "envelope"],
            menu_icon="cast",
            default_index=["홈", "연차휴가 계산기", "근로계약서", "임금대장", "임금명세서"].index(st.session_state.current_page),
        )
        
        st.session_state.current_page = selected
    
    # 페이지 렌더링
    if st.session_state.current_page == "홈":
        render_home_page()
    elif st.session_state.current_page == "연차휴가 계산기":
        render_annual_leave_calculator()
    elif st.session_state.current_page == "근로계약서":
        render_employment_contract_form()
    elif st.session_state.current_page == "임금대장":
        render_payroll_ledger_ui()
    elif st.session_state.current_page == "임금명세서":
        render_pay_statement_ui()
    
    # 푸터
    st.markdown(
        """
        <div class="footer">
            <p>© 2025 HR 관리 시스템 | 모든 권리 보유</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# 홈 페이지 렌더링
def render_home_page():
    st.markdown('<h1 class="main-header">HR 관리 시스템</h1>', unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class="info-box">
            <h2 class="sub-header">👋 환영합니다!</h2>
            <p>
                HR 관리 시스템은 인사 관리 업무를 효율적으로 처리할 수 있도록 도와주는 종합 솔루션입니다.
                연차휴가 계산, 근로계약서 작성, 임금대장 관리, 임금명세서 생성 등 다양한 기능을 제공합니다.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # 기능 소개
    st.markdown('<h2 class="sub-header">📊 주요 기능</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(
            """
            ### 🗓️ 연차휴가 계산기
            - 입사일 기준 연차휴가 계산
            - 회계연도 기준 연차휴가 계산
            - 연차휴가 발생 테이블 생성
            
            ### 📝 근로계약서
            - 근로계약서 템플릿 제공
            - 맞춤형 근로계약서 작성
            - PDF 형식으로 다운로드
            """
        )
    
    with col2:
        st.markdown(
            """
            ### 💰 임금대장
            - 직원 정보 관리
            - 임금 지급 기록 관리
            - 월별/연간 보고서 생성
            
            ### 💵 임금명세서
            - 개별 임금명세서 생성
            - 일괄 임금명세서 생성
            - PDF 형식으로 다운로드
            """
        )
    
    # 시작하기
    st.markdown('<h2 class="sub-header">🚀 시작하기</h2>', unsafe_allow_html=True)
    
    st.markdown(
        """
        왼쪽 사이드바에서 원하는 기능을 선택하여 시작하세요.
        
        - **연차휴가 계산기**: 직원의 연차휴가를 계산합니다.
        - **근로계약서**: 근로계약서를 작성하고 PDF로 다운로드합니다.
        - **임금대장**: 직원 정보와 임금 지급 기록을 관리합니다.
        - **임금명세서**: 임금명세서를 생성하고 PDF로 다운로드합니다.
        """
    )
    
    # 사용 팁
    st.markdown('<h2 class="sub-header">💡 사용 팁</h2>', unsafe_allow_html=True)
    
    st.info(
        """
        - 모든 데이터는 로컬에 저장되며, 인터넷 연결 없이도 사용할 수 있습니다.
        - PDF 파일은 다운로드 후 인쇄하거나 이메일로 전송할 수 있습니다.
        - 정기적으로 데이터를 백업하는 것을 권장합니다.
        """
    )

if __name__ == "__main__":
    main()
