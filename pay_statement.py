import streamlit as st
import pandas as pd
import numpy as np
import datetime
import os
import sys
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib import colors

# 임금대장 클래스 임포트 (수정됨)
from payroll_ledger import PayrollLedger

class PayStatement:
    """
    임금명세서 생성 클래스
    
    임금명세서 템플릿을 생성하고 PDF로 변환하는 기능을 제공합니다.
    """
    
    def __init__(self):
        """
        임금명세서 생성기 초기화
        """
        # 한글 폰트 등록
        self._register_korean_fonts()
        
        # 임금대장 인스턴스 생성
        self.payroll_ledger = PayrollLedger()
    
    def _register_korean_fonts(self):
        """한글 폰트 등록"""
        # 시스템에 설치된 CJK 폰트 사용
        noto_font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
        wqy_font_path = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
        
        # 폰트 등록
        if os.path.exists(noto_font_path):
            pdfmetrics.registerFont(TTFont('NotoSansCJK', noto_font_path))
            self.font_name = 'NotoSansCJK'
        elif os.path.exists(wqy_font_path):
            pdfmetrics.registerFont(TTFont('WenQuanYiZenHei', wqy_font_path))
            self.font_name = 'WenQuanYiZenHei'
        else:
            # 폰트 파일이 없는 경우 다운로드
            font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static/fonts")
            os.makedirs(font_dir, exist_ok=True)
            
            # NanumGothic 폰트 다운로드 (없는 경우)
            nanum_font_path = os.path.join(font_dir, "NanumGothic.ttf")
            if not os.path.exists(nanum_font_path):
                import urllib.request
                urllib.request.urlretrieve(
                    "https://github.com/naver/nanumfont/raw/master/NanumGothic.ttf",
                    nanum_font_path
                )
            
            # 폰트 등록
            pdfmetrics.registerFont(TTFont('NanumGothic', nanum_font_path))
            self.font_name = 'NanumGothic'
    
    def generate_pay_statement_pdf(self, ledger_id):
        """
        임금명세서 PDF 생성
        
        Args:
            ledger_id (str): 임금 지급 ID
            
        Returns:
            bytes: PDF 파일 바이트 데이터
        """
        # 임금 지급 정보 조회
        payroll = self.payroll_ledger.get_payroll(ledger_id)
        
        if payroll is None:
            return None
        
        # 직원 정보 조회
        employee = self.payroll_ledger.get_employee(payroll["employee_id"])
        
        if employee is None:
            return None
        
        # PDF 생성
        buffer = io.BytesIO()
        
        # PDF 문서 생성
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=20*mm,
            bottomMargin=20*mm
        )
        
        # 스타일 설정
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='Korean',
            fontName=self.font_name,
            fontSize=10,
            leading=14,
            alignment=TA_JUSTIFY
        ))
        styles.add(ParagraphStyle(
            name='KoreanTitle',
            fontName=self.font_name,
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            spaceAfter=10
        ))
        styles.add(ParagraphStyle(
            name='KoreanSubtitle',
            fontName=self.font_name,
            fontSize=12,
            leading=16,
            alignment=TA_LEFT,
            spaceAfter=6
        ))
        styles.add(ParagraphStyle(
            name='KoreanCenter',
            fontName=self.font_name,
            fontSize=10,
            leading=14,
            alignment=TA_CENTER
        ))
        styles.add(ParagraphStyle(
            name='KoreanRight',
            fontName=self.font_name,
            fontSize=10,
            leading=14,
            alignment=TA_RIGHT
        ))
        
        # 문서 내용
        story = []
        
        # 제목
        story.append(Paragraph("임 금 명 세 서", styles['KoreanTitle']))
        story.append(Spacer(1, 10*mm))
        
        # 기본 정보 테이블
        payment_date = pd.to_datetime(payroll["payment_date"]).strftime("%Y년 %m월 %d일")
        payment_period = f"{pd.to_datetime(payroll['payment_period_start']).strftime('%Y-%m-%d')} ~ {pd.to_datetime(payroll['payment_period_end']).strftime('%Y-%m-%d')}"
        
        basic_info_data = [
            ["성명", employee["name"], "부서", employee["department"]],
            ["직급", employee["position"], "지급일", payment_date],
            ["지급기간", payment_period, "지급방법", payroll["payment_method"]]
        ]
        
        basic_info_table = Table(basic_info_data, colWidths=[30*mm, 50*mm, 30*mm, 50*mm])
        basic_info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.font_name, 10),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (2, 0), (2, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ]))
        
        story.append(basic_info_table)
        story.append(Spacer(1, 5*mm))
        
        # 지급 내역 테이블
        story.append(Paragraph("■ 지급 내역", styles['KoreanSubtitle']))
        
        payment_data = [
            ["항목", "금액"],
            ["기본급", f"{payroll['base_salary']:,}원"],
            ["초과근무수당", f"{payroll['overtime_pay']:,}원"],
            ["상여금", f"{payroll['bonus']:,}원"],
            ["식대", f"{payroll['meal_allowance']:,}원"],
            ["교통비", f"{payroll['transportation_allowance']:,}원"],
            ["기타수당", f"{payroll['other_allowances']:,}원"],
            ["총 지급액", f"{payroll['gross_pay']:,}원"]
        ]
        
        payment_table = Table(payment_data, colWidths=[80*mm, 80*mm])
        payment_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.font_name, 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ]))
        
        story.append(payment_table)
        story.append(Spacer(1, 5*mm))
        
        # 공제 내역 테이블
        story.append(Paragraph("■ 공제 내역", styles['KoreanSubtitle']))
        
        deduction_data = [
            ["항목", "금액"],
            ["소득세", f"{payroll['income_tax']:,.0f}원"],
            ["지방소득세", f"{payroll['local_income_tax']:,.0f}원"],
            ["국민연금", f"{payroll['national_pension']:,.0f}원"],
            ["건강보험", f"{payroll['health_insurance']:,.0f}원"],
            ["고용보험", f"{payroll['employment_insurance']:,.0f}원"],
            ["총 공제액", f"{payroll['total_deductions']:,.0f}원"]
        ]
        
        deduction_table = Table(deduction_data, colWidths=[80*mm, 80*mm])
        deduction_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.font_name, 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ]))
        
        story.append(deduction_table)
        story.append(Spacer(1, 5*mm))
        
        # 실수령액
        story.append(Paragraph("■ 실수령액", styles['KoreanSubtitle']))
        
        net_pay_data = [
            ["총 지급액", "총 공제액", "실수령액"],
            [f"{payroll['gross_pay']:,}원", f"{payroll['total_deductions']:,.0f}원", f"{payroll['net_pay']:,.0f}원"]
        ]
        
        net_pay_table = Table(net_pay_data, colWidths=[53*mm, 53*mm, 54*mm])
        net_pay_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), self.font_name, 10),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('ALIGN', (0, 1), (-1, 1), 'RIGHT'),
        ]))
        
        story.append(net_pay_table)
        story.append(Spacer(1, 10*mm))
        
        # 비고
        if payroll["note"]:
            story.append(Paragraph("■ 비고", styles['KoreanSubtitle']))
            story.append(Paragraph(payroll["note"], styles['Korean']))
            story.append(Spacer(1, 10*mm))
        
        # 발행일
        today = datetime.date.today().strftime("%Y년 %m월 %d일")
        story.append(Paragraph(f"발행일: {today}", styles['KoreanRight']))
        story.append(Spacer(1, 5*mm))
        
        # 회사명
        company_name = "주식회사 OOO"  # 회사명은 실제 데이터에서 가져오거나 설정 필요
        story.append(Paragraph(company_name, styles['KoreanCenter']))
        
        # PDF 생성
        doc.build(story)
        
        # 버퍼의 내용을 바이트로 변환
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    def generate_multiple_pay_statements(self, ledger_ids):
        """
        여러 임금명세서 PDF 생성
        
        Args:
            ledger_ids (list): 임금 지급 ID 목록
            
        Returns:
            bytes: PDF 파일 바이트 데이터
        """
        if not ledger_ids:
            return None
        
        # 단일 임금명세서인 경우
        if len(ledger_ids) == 1:
            return self.generate_pay_statement_pdf(ledger_ids[0])
        
        # 여러 임금명세서를 하나의 PDF로 병합
        from PyPDF2 import PdfMerger
        
        merger = PdfMerger()
        
        for ledger_id in ledger_ids:
            pdf_bytes = self.generate_pay_statement_pdf(ledger_id)
            
            if pdf_bytes:
                # 바이트 데이터를 파일 객체로 변환
                pdf_file = io.BytesIO(pdf_bytes)
                merger.append(pdf_file)
        
        # 병합된 PDF 생성
        output = io.BytesIO()
        merger.write(output)
        merger.close()
        
        # 버퍼의 내용을 바이트로 변환
        pdf_bytes = output.getvalue()
        output.close()
        
        return pdf_bytes
    
    def generate_batch_pay_statements(self, year, month):
        """
        월별 임금명세서 일괄 생성
        
        Args:
            year (int): 연도
            month (int): 월
            
        Returns:
            bytes: PDF 파일 바이트 데이터
        """
        # 해당 월의 시작일과 종료일
        start_date = pd.Timestamp(year=year, month=month, day=1)
        if month == 12:
            end_date = pd.Timestamp(year=year+1, month=1, day=1) - pd.Timedelta(days=1)
        else:
            end_date = pd.Timestamp(year=year, month=month+1, day=1) - pd.Timedelta(days=1)
        
        # 해당 월의 임금 지급 기록
        monthly_payrolls = self.payroll_ledger.get_payrolls_by_period(start_date, end_date)
        
        if monthly_payrolls.empty:
            return None
        
        # 임금 지급 ID 목록
        ledger_ids = monthly_payrolls["ledger_id"].tolist()
        
        # 여러 임금명세서 생성
        return self.generate_multiple_pay_statements(ledger_ids)

def render_pay_statement_ui():
    """
    임금명세서 UI 렌더링 함수
    """
    st.title("💵 임금명세서 생성기")
    
    # 임금명세서 인스턴스 생성
    pay_statement = PayStatement()
    
    # 탭 생성
    tabs = st.tabs(["개별 임금명세서", "일괄 임금명세서"])
    
    # 개별 임금명세서 탭
    with tabs[0]:
        st.header("개별 임금명세서 생성")
        
        # 직원 선택
        employees = pay_statement.payroll_ledger.get_all_employees()
        
        if not employees.empty:
            employee_names = employees["name"].tolist()
            employee_ids = employees["employee_id"].tolist()
            
            selected_employee = st.selectbox("직원 선택", employee_names)
            selected_employee_id = employee_ids[employee_names.index(selected_employee)]
            
            # 선택한 직원의 임금 지급 기록
            payrolls = pay_statement.payroll_ledger.get_employee_payrolls(selected_employee_id)
            
            if not payrolls.empty:
                # 임금 지급 기록 선택
                payroll_options = []
                for _, row in payrolls.iterrows():
                    payment_date = pd.to_datetime(row["payment_date"]).strftime("%Y-%m-%d")
                    payroll_options.append(f"{payment_date} (ID: {row['ledger_id']})")
                
                selected_payroll = st.selectbox("임금 지급 기록 선택", payroll_options)
                selected_ledger_id = selected_payroll.split("(ID: ")[1].split(")")[0]
                
                if st.button("임금명세서 생성"):
                    # 임금명세서 생성
                    pdf_bytes = pay_statement.generate_pay_statement_pdf(selected_ledger_id)
                    
                    if pdf_bytes:
                        st.success("임금명세서가 생성되었습니다. 아래 버튼을 클릭하여 다운로드하세요.")
                        
                        # PDF를 base64로 인코딩하여 다운로드 링크 생성
                        b64 = base64.b64encode(pdf_bytes).decode()
                        href = f'<a href="data:application/pdf;base64,{b64}" download="임금명세서_{selected_employee}_{pd.to_datetime(payrolls[payrolls["ledger_id"] == selected_ledger_id]["payment_date"].values[0]).strftime("%Y%m%d")}.pdf">임금명세서 다운로드</a>'
                        st.markdown(href, unsafe_allow_html=True)
                        
                        # PDF 미리보기
                        st.subheader("PDF 미리보기")
                        st.write("PDF 파일이 생성되었습니다. 위 링크를 클릭하여 다운로드하세요.")
                    else:
                        st.error("임금명세서 생성에 실패했습니다.")
            else:
                st.warning("선택한 직원의 임금 지급 기록이 없습니다.")
        else:
            st.warning("등록된 직원이 없습니다. 직원을 먼저 등록해주세요.")
    
    # 일괄 임금명세서 탭
    with tabs[1]:
        st.header("일괄 임금명세서 생성")
        
        # 연도 및 월 선택
        payrolls = pay_statement.payroll_ledger.get_all_payrolls()
        
        if not payrolls.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                years = sorted(list(pd.to_datetime(payrolls["payment_date"]).dt.year.unique()), reverse=True)
                if not years:
                    years = [datetime.date.today().year]
                
                selected_year = st.selectbox("연도", years)
            
            with col2:
                selected_month = st.selectbox("월", list(range(1, 13)), index=datetime.date.today().month - 1)
            
            if st.button("일괄 임금명세서 생성"):
                # 일괄 임금명세서 생성
                pdf_bytes = pay_statement.generate_batch_pay_statements(selected_year, selected_month)
                
                if pdf_bytes:
                    st.success("일괄 임금명세서가 생성되었습니다. 아래 버튼을 클릭하여 다운로드하세요.")
                    
                    # PDF를 base64로 인코딩하여 다운로드 링크 생성
                    b64 = base64.b64encode(pdf_bytes).decode()
                    href = f'<a href="data:application/pdf;base64,{b64}" download="일괄_임금명세서_{selected_year}년_{selected_month}월.pdf">일괄 임금명세서 다운로드</a>'
                    st.markdown(href, unsafe_allow_html=True)
                    
                    # PDF 미리보기
                    st.subheader("PDF 미리보기")
                    st.write("PDF 파일이 생성되었습니다. 위 링크를 클릭하여 다운로드하세요.")
                else:
                    st.warning(f"{selected_year}년 {selected_month}월에 임금 지급 기록이 없습니다.")
        else:
            st.warning("임금 지급 기록이 없습니다. 임금 지급 기록을 먼저 등록해주세요.")

if __name__ == "__main__":
    render_pay_statement_ui()
