import yfinance as yf

# KOSPI 지수 티커
kospi = yf.Ticker("^KS11")

# 최근 종가 데이터를 가져옵니다.
data = kospi.history(period="1d")
print(data['Close'])
