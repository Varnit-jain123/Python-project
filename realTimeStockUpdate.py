import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(page_title="Stock Market Dashboard")

st.title("Basic Stock Market Dashboard")
st.markdown("Welcome! Enter a **stock ticker symbol** below (like `AAPL`, `GOOGL`, or `MSFT`) to see its recent market data and price chart.")

ticker = st.text_input("Stock Ticker", value="AAPL", help="Type the stock symbol you want to track (e.g., AAPL for Apple Inc.)").upper()

end_date = datetime.today().date()
start_date = end_date - timedelta(days=365)

if ticker:
    with st.spinner(f"Fetching data for `{ticker}`..."):
        data = yf.download(ticker, start=start_date, end=end_date)

    if not data.empty:
        st.subheader(f" Stock Price Chart for **{ticker}**")
        st.line_chart(data["Close"])

        latest = data.iloc[-1]

        st.markdown("###  Latest Market Info")
        st.write(f"**Date:** {data.index[-1].date()}")
        st.write(f"**Open:** ${float(latest['Open']):.2f}")
        st.write(f"**Close:** ${float(latest['Close']):.2f}")
        st.write(f"**High:** ${float(latest['High']):.2f}")
        st.write(f"**Low:** ${float(latest['Low']):.2f}")
        st.write(f"**Volume:** {int(latest['Volume']):,} shares")

        with st.expander(" Show Raw Historical Data"):
            st.dataframe(data.style.format({
                "Open": "${:.2f}",
                "High": "${:.2f}",
                "Low": "${:.2f}",
                "Close": "${:.2f}",
                "Volume": "{:,}"
            }))
    else:
        st.error(" No data found for that ticker. Please double-check the symbol and try again.")
