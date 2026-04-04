import yfinance as yf
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

#----------RSI FUNCTIONS--------------
def compute_RSI(data, window=14):
    delta = data.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    # Use exponential moving average (better)
    avg_gain = gain.ewm(alpha=1/window, min_periods=window).mean()
    avg_loss = loss.ewm(alpha=1/window, min_periods=window).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

#-------------------UI-------------------------------------------------------------------------
st.title("STOCK VIEWER BY SHIELDERS")
ticker = st.text_input("Enter Stock Ticker(eg,RELIANCE.NS)","RELIANCE.NS")
timeframe = st.selectbox("Select Time Period",["3mo","6mo","1y","3y","5y"])

if ticker:
    df = yf.download(ticker,period = timeframe)
    if df.empty:
        st.error("Invalid ticker or no data found")
    else:
        st.write("Raw data",df.tail())
        st.subheader("Closing Price Chart")
        
        #-----------------Feature Engineering------------------------------
        df['MA10'] = df['Close'].rolling(window=10).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()
        df['RSI'] = compute_RSI(df['Close'])
        df = df.dropna()
        
        current_price = float(df['Close'].iloc[-1,0])
        rsi_value = df['RSI'].iloc[-1]
        col1, col2 = st.columns(2)
        col1.metric("Current Price", f"{current_price:.2f}")
        col2.metric("RSI", f"{rsi_value:.2f}")
        
        if df['MA10'].iloc[-1] > df['MA50'].iloc[-1]:
            trend = "UPTREND"
        else:
            trend = "DOWNTREND"
        
        rsi_value = float(df['RSI'].iloc[-1])
        if rsi_value > 70:
            rsi_signal ="Overbought (SELL)"
        elif rsi_value < 30:
            rsi_signal = "Oversold (BUY)"
        else:
            rsi_signal ="Neutral (HOLD)"
        
        if df['MA10'].iloc[-1] > df['MA50'].iloc[-1] and rsi_value < 30:
            final_signal = "BUY"
        elif df['MA10'].iloc[-1] < df['MA50'].iloc[-1] and rsi_value > 70:
            final_signal = "SELL"
        else:
            final_signal = "HOLD OR (MARKET IS CURRENTLY UNCERTAIN TO BUY OR SELL)"
        df = df.dropna()
        
        #-----PRICE + MA PLOT----------------------------------------------
        
        st.subheader("Price with Moving Averages")
        plt.clf()
        plt.figure(figsize=(10,5))
        plt.plot(df['Close'],label='Close Price')
        plt.plot(df['MA10'],label='MA10')
        plt.plot(df['MA50'],label ='MA50')
        
        plt.xlabel("Date")
        plt.ylabel("Price")
        
        plt.legend()
        plt.grid(True)
        st.pyplot(plt.gcf())
        
        #-----RSI PLOT-------------------------------------------------------------------------------
        st.subheader("RSI Indicator")
        
        plt.figure(figsize = (10,3))
        plt.plot(df['RSI'],label ='RSI',color = 'purple')
        plt.axhline(70, linestyle='--') #overbought
        plt.axhline(30, linestyle ='--') #oversold
        
        plt.legend()
        st.pyplot(plt.gcf())
        
        #-------Stock Analysis--------------------------------------------------------------------
        st.subheader("Analysis")
        col1,col2 = st.columns(2)
        with col1:
           price_fig = plt.figure(figsize=(6,4))
           plt.plot(df['Close'], label='Close Price')
           plt.plot(df['MA10'], label='MA10')
           plt.plot(df['MA50'], label='MA50')
           plt.legend()
           plt.grid(True)
           st.pyplot(price_fig)

           rsi_fig = plt.figure(figsize=(6,3))
           plt.plot(df['RSI'], label='RSI')
           plt.axhline(70, linestyle='--')
           plt.axhline(30, linestyle='--')
           plt.legend()
           plt.grid(True)
           st.pyplot(rsi_fig)
           
        with col2:
            if "BUY" in final_signal:
                st.success(final_signal)
            elif "SELL" in final_signal:
                st.error(final_signal)
            else:
                st.warning(final_signal)
        
            st.write(f"Trend:{trend}")
            st.write(f"RSI Signal:{rsi_signal}")
            st.subheader("Closing Price Chart")
            st.write(f"Final Recommendation: {final_signal}")
            