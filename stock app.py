# 파일명: stock app.py (또는 money.py)

import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

# -----------------------------------------------------
# 💡 핵심 데이터 호출 함수 (2단계 검증 완료)
# -----------------------------------------------------

def get_stock_data(code, days=90):
    """
    종목 코드 (예: 005930.KS)와 기간(일)을 받아 주가 데이터를 가져오는 함수.
    """
    TODAY = datetime.date.today().strftime('%Y-%m-%d')
    START_DATE = (datetime.date.today() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
    
    # 한국 주식 코스피(.KS) 기본 처리
    if not (code.endswith('.KS') or code.endswith('.KQ')):
        code += '.KS'
    
    try:
        ticker_data = yf.Ticker(code)
        df_stock = ticker_data.history(start=START_DATE, end=TODAY)
        
        if not df_stock.empty:
            df_clean = df_stock[['Close', 'Volume']].rename(columns={
                'Close': '종가',
                'Volume': '거래량'
            })
            df_clean['변화율 (%)'] = df_clean['종가'].pct_change().mul(100).round(2)
            
            return df_clean, ""
        else:
            return pd.DataFrame(), f"⚠️ 종목 코드 {code}에 대한 데이터가 없거나 잘못된 코드입니다."
            
    except Exception:
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
    stock_code = st.text_input("종목 코드 입력 (예: 005930):", "005930").strip()
    days_input = st.slider("조회 기간 (일):", min_value=30, max_value=365, value=90)
    
    if st.button("주가 검색 및 분석"):
        
        with st.spinner(f"종목 코드 {stock_code}의 {days_input}일 데이터를 불러오는 중..."):
            df_stock, status_message = get_stock_data(stock_code, days_input)

        if not df_stock.empty:
            st.success("✅ 주가 데이터 로딩 완료")
            
            st.subheader(f"📊 {stock_code} ({days_input}일) 주가 정보")
            
            # 기간 내 최고가/최저가 정보 추출
            max_price = df_stock['종가'].max()
            min_price = df_stock['종가'].min()
            
            # 메트릭 표시 (Line 82 근처 문법 오류 수정)
            st.metric(label="최근 종가", 
                      value=f"{df_stock['종가'].iloc[-1]:,}", 
                      # ❗ SyntaxError 방지를 위해 f-string을 완벽하게 처리
                      delta=f"{df_stock['변화율 (%)'].iloc[-1]:.2f}%") 
            
            # st.info 문법 오류 수정
            st.info(f"기간 내 최고 종가: {max_price:,}원 | 최저 종가: {min_price:,}원")
            
            # 종가 차트
            st.subheader("기간별 종가 변화")
            st.line_chart(df_stock['종가'])
            
            st.subheader("원천 데이터")
            st.dataframe(df_stock, use_container_width=True)
            
        else:
            st.error(status_message)
            st.info("💡 코스피 종목은 '000000' 형식으로 입력해주세요.")