# KRX

### 사용방법

1. UPDATE

    ```python manage.py import_kospi_data.py```</br>
    기존 데이터에서 가장 최근 데이터까지 SQL에 업데이트

### Packages

- yfinance
    - 1996년 12월 11일 부터 데이터 존재. 그래서 1980년 1월 4일 코스피 100부터 시작되는 데이터가 존재하지 않음

- Celery 
    - models 안에 데이터를 매일 업데이트 하기 위해 사용

- 참고사항

    - 나중에 옛날 컴퓨터가 없던 시절 데이터는 수기로 SQL 안에 넣어야 할 듯</br>
      index.krx.co.kr 여기에 저장


### Implemented Features

- During login, users can obtain a token using either a **username or email** along with a **password**.
  
  Originally, it was only possible to log in with a **username and password**, but this has been customized.

- Test User:

  - Username**: test1
  - Email**: test1@gmail.com
  - Password**: user@123