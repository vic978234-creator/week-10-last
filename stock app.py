# 파일명: stock_app.py (또는 money.py)

import streamlit as st
import yfinance as yf # yahoofinance가 yf 기능을 사용하기 위해 함께 import
import pandas as pd
import datetime

# -----------------------------------------------------
# 💡 2단계에서 검증된 핵심 데이터 호출 함수 (YFinance 기반)
# -----------------------------------------------------

def get_stock_data(code, days=90):
    """
    종목 코드 (예: 005930.KS)와 기간(일)을 받아 주가 데이터를 가져오는 함수.
    """
    # YFinance는 yyyy-mm-dd 형식의 문자열 날짜를 사용합니다.
    TODAY = datetime.date.today().strftime('%Y-%m-%d')
    START_DATE = (datetime.date.today() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
    
    # 한국 주식 코스피(.KS) 기본 처리
    if not (code.endswith('.KS') or code.endswith('.KQ')):
        code += '.KS'
    
    try:
        # Ticker 객체 생성 및 기간 데이터 다운로드
        ticker_data = yf.Ticker(code)
        df_stock = ticker_data.history(start=START_DATE, end=TODAY)
        
        if not df_stock.empty:
            # 필요한 컬럼만 정리 및 이름 변경
            df_clean = df_stock[['Close', 'Volume']].rename(columns={
                'Close': '종가',
                'Volume': '거래량'
            })
            # 변화율 컬럼 추가
            df_clean['변화율 (%)'] = df_clean['종가'].pct_change().mul(100).round(2)
            
            return df_clean, ""
        else:
            return pd.DataFrame(), f"⚠️ 종목 코드 {code}에 대한 데이터가 없거나 잘못된 코드입니다."
            
    except Exception:
        # 데이터 가져오기 실패 시 오류 메시지 반환
        return pd.DataFrame(), f"❌ 데이터를 가져올 수 없습니다. 종목 코드를 확인하세요."


# -----------------------------------------------------
# 💡 Streamlit UI (사용자 인터페이스) 시작
# -----------------------------------------------------

st.set_page_config(layout="wide")
st.title("💰 주식 주가 변화 분석기")
st.markdown("---")

# 종목 코드 입력 UI
col1, col2 = st.columns([1, 2])
with col1:
    # 사용자 편의를 위해 .KS를 빼고 숫자만 입력하도록 안내합니다.
    stock_code = st.text_input("종목 코드 입력 (예: 005930):", "005930").strip()
    days_input = st.slider("조회 기간 (일):", min_value=30, max_value=365, value=90)
    
    if st.button("주가 검색 및 분석"):
        
        # 2. 로딩 스피너 표시
        with st.spinner(f"종목 코드 {stock_code}의 {days_input}일 데이터를 불러오는 중..."):
            # 3. 2단계에서 만든 함수 호출
            df_stock, status_message = get_stock_data(stock_code, days_input)

        # 4. 결과에 따른 UI 표시
        if not df_stock.empty:
            st.success("✅ 주가 데이터 로딩 완료")
            
            st.subheader(f"📊 {stock_code} ({days_input}일) 주가 정보")
            
            # 기간 내 최고가/최저가 정보 추출
            max_price = df_stock['종가'].max()
            min_price = df_stock['종가'].min()
            
            # 메트릭 표시 (최근 종가 및 변화율)
            st.metric(label="최근 종가", 
                      value=f"{df_stock['종가'].iloc[-1]:,}", 
                      delta=f"{df