import streamlit as st
from audiorecorder import audiorecorder
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from whisper_stt import STT
from whisper_stt import ask_gpt
from whisper_stt import TTS
import streamlit as st
import numpy as np
from datetime import datetime
from PIL import Image

def main():
    st.set_page_config(
        page_title="we-are-crawling-the-trends",
        layout="wide")

    # session state 초기화
    if "chat" not in st.session_state:
        st.session_state["chat"] = []

    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "system", "content": "You are a thoughtful assistant. Respond to all input in 25 words and answer in korea"}]

    if "check_audio" not in st.session_state:
        st.session_state["check_audio"] = []
    
    st.header("트렌드를 분석하는 <11조>입니다.💫")
    st.markdown("---")

    ### 칼럼
    flag_start = False

    col1, col2 =  st.columns([3,5])
    with col1:
        st.subheader("어떤 것이 궁금한가요?")
        # 음성 녹음 아이콘
        audio = audiorecorder("🐣여기를 클릭하여 말하십쇼~🐣", "🐣여기를 클릭하여 끝내십쇼~🐣")
        if len(audio) > 0 and not np.array_equal(audio,st.session_state["check_audio"]):
            # 음성 재생 
            st.audio(audio.tobytes())

            # 음원 파일에서 텍스트 추출
            question = STT(audio)
            # 채팅을 시각화하기 위해 질문 내용 저장
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"]+ [("user",now, question)]
            # GPT 모델에 넣을 프롬프트를 위해 질문 내용 저장
            st.session_state["messages"] = st.session_state["messages"]+ [{"role": "user", "content": question}]
            # audio 버퍼 확인을 위해 현 시점 오디오 정보 저장
            st.session_state["check_audio"] = audio
            flag_start =True
        img1 = Image.open('tell-me.jpg')
        st.image(img1,width=200)

    with col2:
        st.subheader("질문/답변")
        if flag_start:
            #ChatGPT에게 답변 얻기
            response = ask_gpt(st.session_state["messages"], "gpt-3.5-turbo")

            # GPT 모델에 넣을 프롬프트를 위해 답변 내용 저장
            st.session_state["messages"] = st.session_state["messages"]+ [{"role": "system", "content": response}]

            # 채팅 시각화를 위한 답변 내용 저장
            now = datetime.now().strftime("%H:%M")
            st.session_state["chat"] = st.session_state["chat"]+ [("bot",now, response)]

            # 채팅 형식으로 시각화 하기
            for sender, time, message in st.session_state["chat"]:
                if sender == "user":
                    st.write(f'<div style="display:flex;align-items:center;"><div style="background-color:#007AFF;color:white;border-radius:12px;padding:8px 12px;margin-right:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")
                else:
                    st.write(f'<div style="display:flex;align-items:center;justify-content:flex-end;"><div style="background-color:lightgray;border-radius:12px;padding:8px 12px;margin-left:8px;">{message}</div><div style="font-size:0.8rem;color:gray;">{time}</div></div>', unsafe_allow_html=True)
                    st.write("")
            
            # gTTS 를 활용하여 음성 파일 생성 및 재생
            TTS(response)

    ### 사이드바
    import plotly.graph_objects as go
    import pandas as pd
    import yfinance as yf

    st.sidebar.title("Stock Chart")
    ticker = st.sidebar.text_input("Enter a ticker (e. g. AAPL)", value = "AAPL")
    st.sidebar.markdown('Tickers Link : [All Stock Symbols](https://stockanalysis.com/stocks/)')
    start_date = st.sidebar.date_input("시작 날짜: ", value = pd.to_datetime("2023-01-01"))
    end_date = st.sidebar.date_input("종료 날짜: ", value = pd.to_datetime("2023-07-28"))

    # ticker 종목의 시작~종료 날짜 사이의 가격변화를 데이터로 보여줌
    data = yf.download(ticker, start= start_date, end= end_date)
    st.dataframe(data)

    # Line Chart, Candle Stick 중 선택
    chart_type = st.sidebar.radio("Select Chart Type", ("Candle_Stick", "Line"))
    candlestick = go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'])
    line = go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close')

    if chart_type == "Candle_Stick":
        fig = go.Figure(candlestick)
    elif chart_type == "Line":
        fig = go.Figure(line)
    else:
        st.error("error")

    fig.update_layout(title=f"{ticker} Stock {chart_type} Chart", xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig)

    with st.sidebar:
        st.subheader("체크박스들")
        st.checkbox("checkbox1")
        st.checkbox("checkbox2")
        st.markdown("---")

if __name__=="__main__":
    main()